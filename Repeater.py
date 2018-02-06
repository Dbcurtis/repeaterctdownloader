#!/usr/bin/env python3
""" To Be Done """
import sys
import userinput
import getports
import commandreader
import controller
import utils

_DEBUGGING = False


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
                break  #exit when file read
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
    """_cmdloop(c)

    c is a controller.
    prints the exit command info,
    Accepts a command from the user, sends it to the controller and displays the result.

    Loop exits on a command starting with a q or e
    """
    print("Quit or Exit to exit command mode")
    while 1:
        cmd = input("input>").cmd.strip().upper()
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
            return False

        def _errmsg(ignore):
            print("only type one of Q, M, U, or F")
            return True

        cmddisptch = {
            'q':_nodop,
            'm':send_users_cmds,
            'u':do_utility_cmds,
            'f':send_file,
        }

        _loop_ctl = True
        while _loop_ctl:
            _response = input("Type 'Q' to quit\n"
                              "Type 'M' for manual commands\n"
                              "type 'U' for Utility operations\n"
                              "Type 'F' for file transfer (Q/F/M/U)?>").strip().lower()[0:1]
            _loop_ctl = cmddisptch.get(_response, _errmsg)(_response)
    finally:
        _ui.close()

if __name__ == '__main__':

    try:
        main()
    except(Exception, KeyboardInterrupt) as exc:
        sys.exit(str(exc))
