#!/usr/bin/env python3
"""controller.py

Module to send commands to a repeater controller over a serial line.


"""

import sys
import os
#from typing import Any, Union, Tuple, Callable, TypeVar, Generic, Sequence, Mapping, List, Dict, Set, Deque, Iterable
from typing import Any, Tuple, List, Dict
from os import path
import logging
import logging.handlers
import re
from datetime import datetime
from time import time
import userinput


LOGGER = logging.getLogger(__name__)

LOG_DIR = os.path.dirname(os.path.abspath(__file__)) + '/logs'
LOG_FILE = '/controller'

def STRING_2_BYTE(a): return bytearray([ord(s) for s in a])
def BYTE_2_STRING(a): return "".join([chr(i) for i in a if i != 13])


def _remove_comment(_cmdline: str) -> str:
    _sans_comment: str = _cmdline.split('\n', 1)  # remove trailing new line
    _sans_comment = _sans_comment[0].split(';', 1)  # remove trailing comment
    return _sans_comment[0].split()


def _none():
    pass


class Controller:
    """Controller Class supports communication of commands to the controller

    c = Controller(ui)
    insantiates a controller using a UserInput object(ui)

    sets up the logging files.  if infil=foo.txt, the command
    log file will be named
    foo.cmdlog.txt and the execution log will be named
    foo.exelog.txt

    The command log is simply the commands that were sent to the controller
    The execution log is a copy of the commands sent and the responses.

    Once the Contoller is instantiated, it needs to be opened before
     use. Closed after use.

    The controller replys are sent to stdout as well as to the logging files

    c=Controller(ui)
    c.open()
    c.sendcmd("009 ;get the matrix")
    c.close()
    """

    _errPat: re.Pattern = re.compile(r".*error:.*", re.I | re.DOTALL)
    _fnPat: re.Pattern = re.compile(r'(.+)\.txt$', re.I)
    #Is_Result_Error = lambda a: Controller._errPat.search(a)

    _introMsg = """
;-------------
; File: {}, Created on: {} UTC
;-----------------
"""
    _timeFmt: str = '%Y%m%d, %H:%M:%S'

    @staticmethod
    def _returnsame(_a: Any) -> Any:
        return _a

    # get the port id and the logging file ids
    def __init__(self, uiIn: userinput.UserInput):
        """__init__(uiIn)

        uiIn is a UserInput object that has defined a file name as input and a
        serial port to be opened to the controller

        If the uiIn.inputfn is blank, then the default file name of 'test.txt' is used
        """

        _in_file_name: str = uiIn.inputfn.strip()
        if not _in_file_name:
            _in_file_name = 'test.txt'

        _ = Controller._fnPat.search(_in_file_name)
        _filename: bool = _ and _.group(1)
        if not _filename:
            print("Filename must end in txt, using 'test.txt'")
            _filename = 'test.txt'
        self.ui: userinput.UserInput = uiIn
        self.s_port = uiIn.serial_port
        self.cmd: str = ""
        self.atts: Dict[str, Any] = {}
        self.atts['cmd_logfile_name'] = _filename + '.cmdlog.txt'
        self.atts['cmd_errfile_name'] = _filename + '.exelog.txt'
        self.atts['is_files_open'] = False
        self.atts['isOpen'] = False
        self.atts['last_response'] = ""
        self.atts['last_cmd'] = ""
        self.atts['last_displayed'] = ""
        self.atts['last_logged'] = ""
        self.atts['cmd_log_file'] = None
        self.atts['cmd_err_file'] = None
        self.atts['when_opened'] = None
        self.atts['open_time'] = None
        self.ctrl_prompt = self.ui.controller_type.newcmd_dict.get('prompt')
        self._byte_string_ifd = {
            True: BYTE_2_STRING,
            False: Controller._returnsame,
        }

    def __str__(self) -> str:
        return f'[Controller: {str(self.atts["is_files_open"])}, {str(self.atts["isOpen"])}, {str(self.ui)}]'

    def __repr__(self) -> str:
        return f'[Controller: {str(self.s_port.isOpen())}, {str(self.atts["is_files_open"])}, {str(self.atts["isOpen"])}, {str(self.ui)}]'

    def open(self) -> bool:
        """open()

        opens the controller, the serial port and the logging files
        sets isFilesOpen if logging files opened correctly
        sets isOpen if the Controller opened correctly

        returns True if the controller opened (both the files and the serial port), false
        otherwise
        """

        if self.s_port.isOpen():
            self.s_port.close()
        self.atts['is_files_open'] = False
        result: bool = False
        try:
            cmd_log_paths = path.abspath(self.atts['cmd_logfile_name'])
            cmd_err_paths = path.abspath(self.atts['cmd_errfile_name'])
            self.atts['cmd_log_file'] = open(
                self.atts['cmd_logfile_name'], 'w', encoding='utf-8')
            self.atts['cmd_err_file'] = open(
                self.atts['cmd_errfile_name'], 'w', encoding='utf-8')
            self.atts['when_opened'] = datetime.now().strftime(
                Controller._timeFmt)
            self.atts['open_time'] = time()
            self.atts['cmd_log_file'].write(Controller._introMsg.format(
                cmd_log_paths, self.atts['when_opened']))
            self.atts['cmd_err_file'].write(Controller._introMsg.format(
                cmd_err_paths, self.atts['when_opened']))
            self.atts['is_files_open'] = True
            self.s_port.open()
            self.atts['isOpen'] = True
            result = True
        except IOError:
            _e = sys.exc_info()[0]
            result = False
            #self.isOpen = False
            self.atts['isOpen'] = False
            print("controller did not open! {}\n".format(_e))

        return result

    def _cnvtcmd(self, cmdin: Any) -> Any:
        return self._byte_string_ifd.get(isinstance(cmdin, bytes))(cmdin)

    def sendcmd(self,
                cmdin,
                display=True,
                log_it=True,
                echoit=False,
                select_it=lambda a: True,
                format_it=lambda a: (a, {})) -> bool:
        """sendcmd(cmdin, display=TF, log_it=TF, echo_it=TF, select_it=TF, format_it=TF)

        Logs the command as provided in the execution log with the results
        of the command.
        It removes the comments and spaces from the command so that it only
        sends the necessisary data.
        blank commands are ignored.

        Sends the command through the serial port and waits for the
        controller response.

        If display is True, the command and the controllers response is printed

        If logIt is True, the commands and the responses are logged
        (subject to selectIt)
        selectIt is a lambda that if it returns true, will cause the
         response to be logged.

           A typlical use of selectIt is: 1) TBD

        formatIt is a lambda that formats the response before logging it

        echo_it is a TF that if True then, TBD

        returns a True if command executed ok, false otherwise
        """
        # pylint: disable=R0914
        # pylint: disable=R0913
        result: bool = True
        cmd = self._cnvtcmd(cmdin)

        def _write_logs():
            self.atts['cmd_log_file'].write(
                cmd + "\n")  # write to command log file
            # write to execution log file
            self.atts['cmd_err_file'].write(cmd + "\n")

        _if_log: Dict[bool, Callable] = {
            True: _write_logs,
            False: _none,
        }
        _if_log.get(log_it)()

        _new_cmd_list = _remove_comment(cmd)

        if not ''.join(_new_cmd_list).strip():  # ignore blank lines
            #self.last_cmd = ""
            self.atts['last_cmd'] = ""
            return result

        # else:
            # print(''.join(necmd)+"\n")
        _new_cmd_list.append('\r')  # add a new line character
        newcmd = ''.join(_new_cmd_list)
        self.atts['last_cmd'] = newcmd

        if not echoit:
            self.s_port.flushInput()  # deprecated, use reset_input_buffer()
            # print(newcmd)
            _saved_to = self.s_port.timeout  # speed up the reads
            self.s_port.timeout = 0.2
            self.s_port.write(STRING_2_BYTE(newcmd))
            _in_list = []
            _cnt: int = 100
            while _cnt > 0:  # keep reading input until the controller
                # prompt (i.e. DTMF>) is seen.
                # Remember the timeout changes with baud rate
                # should get data atleast every timeout seconds
                _in_list.append(BYTE_2_STRING(self.s_port.dread(9999)))
                _cnt += -1
                if ''.join(_in_list).endswith(self.ctrl_prompt):
                    break

            self.s_port.timeout = _saved_to
            #rnok = Controller._errPat.search(''.join(inList))
            if Controller._errPat.search(''.join(_in_list)):  # rnok:
                _in_list.append("******************E R R O R" +
                                "****************\n" + self.ctrl_prompt)
                result = False
            response = ''.join(_in_list)
        else:
            response = newcmd

        self.atts['last_response'] = response

        def _print_response():
            self.atts['last_displayed'] = response
            print(response)

        _if_display = {
            True: _print_response,
            False: _none,
        }
        _if_display.get(display)()

        def _log_it1():
            self.atts['last_logged'] = response
            self.atts['cmd_err_file'].write(format_it(response)[0])

        if_selective_log = {
            True: _log_it1,
            False: _none,
        }
        if_selective_log.get(log_it and select_it(response))()

        return result

    def close(self):
        """close()

        Closes the controller, the logging files, and the serial port
        """
        if self.s_port.isOpen():
            self.s_port.close()
        #self.isOpen = False
        self.atts['isOpen'] = False
        if self.atts['is_files_open']:
            try:
                self.atts['cmd_log_file'].close()
            except IOError:
                pass
            try:
                self.atts['cmd_err_file'].close()
            except IOError:
                pass
            self.atts['is_files_open'] = False


if __name__ == '__main__':
    if not os.path.isdir(LOG_DIR):
        os.mkdir(LOG_DIR)

    LF_HANDLER = logging.handlers.RotatingFileHandler(
        ''.join([LOG_DIR, LOG_FILE, ]),
        maxBytes=10000,
        backupCount=5,
    )
    LF_HANDLER.setLevel(logging.DEBUG)
    LC_HANDLER = logging.StreamHandler()
    LC_HANDLER.setLevel(logging.DEBUG)  # (logging.ERROR)
    LF_FORMATTER = logging.Formatter(
        '%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s')
    LC_FORMATTER = logging.Formatter('%(name)s: %(levelname)s - %(message)s')
    LC_HANDLER.setFormatter(LC_FORMATTER)
    LF_HANDLER.setFormatter(LF_FORMATTER)
    THE_LOGGER = logging.getLogger()
    THE_LOGGER.setLevel(logging.DEBUG)
    THE_LOGGER.addHandler(LF_HANDLER)
    THE_LOGGER.addHandler(LC_HANDLER)
    THE_LOGGER.info('controller executed as main')
    # LOGGER.setLevel(logging.DEBUG)

    UII = userinput.UserInput()

    try:
        def _cmdloop(_c):
            print("Quit or Exit to exit command mode")
            while 1:
                cmd = input("input>")
                cmd = cmd.strip().upper()
                if cmd.startswith('Q') or cmd.startswith('E'):
                    print("Exiting command input mode...")
                    break
                _c.sendcmd(cmd)

        def _send_users_cmds(_ui):
            """ test """
            _ui.open()
            _c = Controller(_ui)
            _c.open()
            try:
                _cmdloop(_c)
                _c.close()
            finally:
                if _ui.serial_port.isOpen():
                    _ui.serial_port.close()
                _c.close()

        UII.request()
        _send_users_cmds(UII)
        UII.close()

    except(Exception, KeyboardInterrupt) as exc:
        UII.close()
        sys.exit(exc)
