#!/usr/bin/env python3
""" TO BE SUPPLIED
"""

import sys
import re
from datetime import datetime
from os import path
from time import time
import userinput


#def call_clsinit(*args, **kwargs):
    #cls = type(*args, **kwargs)
    #cls._clsinit()
    #return cls;

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

    _errPat = re.compile(r".*error:.*", re.I | re.DOTALL)
    _fnPat = re.compile(r'(.+)\.txt$', re.I)
    String_2_Byte = lambda a: bytearray([ord(s) for s in a])
    Byte_2_String = lambda a: "".join([chr(i) for i in a if i != 13])
    #Is_Result_Error = lambda a: Controller._errPat.search(a)

    _introMsg = """
;-------------
; File: %s, Created on: %s UTC
;-----------------
"""
    _timeFmt = '%Y%m%d, %H:%M:%S'


    @staticmethod
    def _returnsame(_a):
        return _a

    def __init__(self, uiIn):  # get the port id and the logging file ids
        """__init__(uiIn)

        uiIn is a UserInput object that has defined a file name as input and a
        serial port to be opened to the controller

        If the uiIn.inputfn is blank, then the defualt file name of 'test.txt' will be used
        """
        _in_file_name = uiIn.inputfn.strip()
        if not _in_file_name:
            _in_file_name = 'test.txt'

        _ = Controller._fnPat.search(_in_file_name)
        _filename = _ and _.group(1)
        if not _filename:
            print("Filename must end in txt, using 'test.txt'")
            _filename = 'test.txt'
        self.cLfn = _filename + '.cmdlog.txt'
        self.cEfn = _filename + '.exelog.txt'
        self.sp = uiIn.serial_port
        self.isFilesOpen = False
        self.isOpen = False
        self.ui = uiIn
        self.cmd = ""
        self.last_response = ""
        self.last_cmd = ""
        self.last_displayed = ""
        self.last_logged = ""
        self.cLFile = None
        self.cEFile = None
        self.when_opened = None
        self.openTime = None
        self.ctrl_prompt = self.ui.controller_type.cmdDict.get('prompt')
        self._byte_string_ifd = {
            True: Controller.Byte_2_String,
            False: Controller._returnsame,
        }

    def __str__(self):
        return '[Controller: %s]' % (str(self.isFilesOpen) + ", " + \
        str(self.isOpen) + ', ' + str(self.ui))

    def __repr__(self):
        return '[Controller: %s]' % (str(self.sp.isOpen()) + ', ' + \
        str(self.isFilesOpen) + \
        ", " + str(self.isOpen) + ', ' + str(self.ui))


    def open(self):
        """open()

        opens the controller, the serial port and the logging files
        sets isFilesOpen if logging files opened correctly
        sets isOpen if the Controller opened correctly

        returns True if the controller opened (both the files and the serial port), false
        otherwise
        """

        if self.sp.isOpen():
            self.sp.close()
        self.isFilesOpen = False
        result = False
        try:
            cLPathS = path.abspath(self.cLfn)
            cEPathS = path.abspath(self.cEfn)
            self.cLFile = open(self.cLfn, 'w', encoding='utf-8')
            self.cEFile = open(self.cEfn, 'w', encoding='utf-8')
            self.when_opened = datetime.now().strftime(Controller._timeFmt)
            self.openTime = time()
            self.cLFile.write(Controller._introMsg % (cLPathS, self.when_opened))
            self.cEFile.write(Controller._introMsg % (cEPathS, self.when_opened))
            self.isFilesOpen = True
            self.sp.open()
            self.isOpen = True
            result = True
        except:
            _e = sys.exc_info()[0]
            result = False
            self.isOpen = False
            print("controller did not open! %s\n" % _e)

        return result

    def _cnvtcmd(self, cmdin):
        return self._byte_string_ifd.get(isinstance(cmdin, bytes))(cmdin)

    def sendcmd(self, cmdin,  \
        display=True, \
        log_it=True, \
        echoit=False, \
        select_it=lambda a: True, \
        format_it=lambda a: (a, {})):
        """sendcmd(cmdin, display=TF, log_it=TF, echo_it=TF, select_it=TF, format_it=TF

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

        returns a True if command executed ok, false otherwise
        """

        result = True
        cmd = self._cnvtcmd(cmdin)

        #print(cmd) # display command on window
        if log_it:
            self.cLFile.write(cmd + "\n")  # write to command log file
            self.cEFile.write(cmd + "\n")  # write to execution log file

        _sans_comment = cmd.split('\n', 1)  # remove trailing new line
        _sans_comment = _sans_comment[0].split(';', 1)  # remove trailing comment
        necmd = _sans_comment[0].split()  # split on spaces
        _ = ''.join(necmd).strip()
        if not _:  # ignore blank lines
            self.last_cmd = ""
            return result

        else:
            String_2_Byte = Controller.String_2_Byte
            Byte_2_String = Controller.Byte_2_String
            #print(''.join(necmd)+"\n")
            necmd.append('\r')  # add a new line
            newcmd = ''.join(necmd)
            self.last_cmd = newcmd
            if not echoit:
                self.sp.flushInput()  # deprecated, use reset_input_buffer()
                #print(newcmd)
                sto = self.sp.timeout  # speed up the reads
                self.sp.timeout = 0.2
                byts = String_2_Byte(newcmd)
                self.sp.write(byts)
                #self.sp.write(String_2_Byte(newcmd))
                _in_list = []
                cnt = 100
                while cnt > 0:  # keep reading input until the controller
                    # prompt (i.e. DTMF>) is seen.
                    # Remember the timeout changes with baud rate
                    #should get data atleast every timeout seconds
                    _in_list.append(Byte_2_String(self.sp.dread(9999)))
                    cnt = cnt - 1
                    if ''.join(_in_list).endswith(self.ctrl_prompt):
                        break

                self.sp.timeout = sto
                #rnok = Controller._errPat.search(''.join(inList))
                if Controller._errPat.search(''.join(_in_list)): #rnok:
                    _in_list.append("******************E R R O R" + \
                    "****************\n"+self.ctrl_prompt)
                    result = False
                response = ''.join(_in_list)
            else:
                response = newcmd

            self.last_response = response
            if display:
                self.last_displayed = response
                print(response)
            if log_it and select_it(response):
                self.last_logged = response
                self.cEFile.write(format_it(response)[0])
        return result

    def close(self):
        """close()

        Closes the controller, the logging files, and the serial port
        """
        if self.sp.isOpen():
            self.sp.close()
        self.isOpen = False
        if self.isFilesOpen:
            try:
                self.cLFile.close()
            except IOError:
                pass
            try:
                self.cEFile.close()
            except IOError:
                pass
            self.isFilesOpen = False

if __name__ == '__main__':
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

        #print('Available comport(s) are: %s' % getports.GetPorts().get())

        UII.request()
        _send_users_cmds(UII)
        UII.close()

    except(Exception, KeyboardInterrupt) as exc:
        UII.close()
        sys.exit(exc)
