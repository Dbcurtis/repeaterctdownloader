#!/usr/bin/env python3
""" To Be Done """
import sys
import os
from typing import Any, Union, Tuple, Callable, TypeVar, Generic, Sequence, Mapping, List, Dict, Set, Deque, Iterable
import logging
import logging.handlers
import userinput
import getports
import commandreader
import controller
import utils

_DEBUGGING = False

LOGGER = logging.getLogger(__name__)

LOG_DIR = os.path.dirname(os.path.abspath(__file__)) + '/logs'
LOG_FILE = '/repeater'


def _send_specified_file(_ui):
    """_send_specified_file()

    ui is a UserInput

    opens the controller, the commandreader, and
    sends each line to the controller.

    """

    _ui.open()
    _c = controller.Controller(_ui)
    _cr = commandreader.CommandReader(_ui)
    _cr.open()
    _c.open()
    try:
        while 1:
            line = _cr.get()
            if line == "":
                break  # exit when file read
            _c.sendcmd(line, echoit=_DEBUGGING)
    finally:
        _c.close()
        _cr.close()
        _ui.close()


def send_file(_ui):
    """send_file()

    asks for a file name and invokes _send_specified_file
    """
    while 1:

        try:
            _ui.inputfn = input("file name to send to repeater?>")
            _send_specified_file(_ui)
            return True
        except OSError:
            print("{} not found".format(_ui.inputfn))
            if input("Abort sendfile Y/N").lower().strip()[0:1] == 'y':
                return False


def _cmdloop(_c):
    """_cmdloop(_c)

    _c is a controller.
    prints the exit command info,
    Accepts a command from the user, sends it to the controller and displays the result.

    Loop exits on a command starting with a q or e
    """
    print("Quit or Exit to exit command mode")
    while 1:
        cmd = input("input>").strip().upper()
        _f = cmd[0:1]
        if _f == 'Q' or _f == 'E':
            print("Exiting command input mode...")
            break
        _c.sendcmd(cmd, echoit=_DEBUGGING)


def send_users_cmds(_ui):
    """sendUsersCmds()

    Opens the ui and controller,
    runs the command loop
    closes the controller and the ui.

    """

    _ui.open()
    _c = controller.Controller(_ui)
    _c.open()
    try:
        _cmdloop(_c)
    finally:
        _c.close()
        _ui.close()
    return True


def do_utility_cmds(_ui):
    """doUtilityCmds()

    Asks for the log file name, opens the ui, and the controller.
    Calls the util processor loop,
    Closes the controller and the ui on exit
    """

    _ui.inputfn = input("input log file name.txt>")
    _ui.open()
    _c = controller.Controller(_ui)
    _c.open()
    try:
        _utils = utils.Utils(_ui, _c)
        _utils.process_loop()
    finally:
        _c.close()
        _ui.close()
    return True


def main():
    """main()

    Identifies the avilable ports, gets user input, sends the specified file (if exists) to
    the controller.

    Prints the command list and processes the user selected command(s)

    """

    _available_ports = getports.GetPorts().get()
    #print("Available serial ports are: {}".format(_available_ports))

    _ui = userinput.UserInput()
    _ui.request()
    try:
        _ui.open()
        _send_specified_file(_ui)

        def _nodop(ignore):
            # pylint: disable=W0613
            return False

        def _errmsg(ignore):
            # pylint: disable=W0613
            print("only type one of Q, M, U, or F")
            return True

        cmddisptch = {
            'q': _nodop,
            'm': send_users_cmds,
            'u': do_utility_cmds,
            'f': send_file,
        }

        _loop_ctl = True
        while _loop_ctl:
            _response = input("Type 'Q' to quit\n"
                              "Type 'M' for manual commands\n"
                              "type 'U' for Utility operations\n"
                              "Type 'F' for file transfer (Q/F/M/U)?>").strip().lower()[0:1]
            _loop_ctl = cmddisptch.get(_response, _errmsg)(_ui)
    finally:
        _ui.close()


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
    THE_LOGGER.info('repeater executed as main')
    # LOGGER.setLevel(logging.DEBUG)

    try:
        main()
    except(Exception, KeyboardInterrupt) as exc:
        sys.exit(str(exc))
