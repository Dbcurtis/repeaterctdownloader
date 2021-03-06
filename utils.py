#!/usr/bin/env python3
""" TBD """

from controller import Controller
from userinput import UserInput
import logging.handlers
import logging
import argparse
import os
import sys
from typing import Any, Union, Tuple, Callable, TypeVar, Generic, Sequence, \
    Mapping, List, Dict, Set, Deque, Iterable

LOGGER = logging.getLogger(__name__)
LOG_DIR = os.path.dirname(os.path.abspath(__file__)) + '/logs'
LOG_FILE: str = '/utils'

IF_N = {True: lambda a: int(a[1:]), False: lambda a: int(a), }
IF_TUP = {True: lambda a: [a], False: lambda a: a, }


def _range_2_list(_arg: Any) -> List[Any]:
    """[_range2_list(arg)]

    Args:
        _arg (Any): [description]

    Returns:
        List[Any]: [description]
    """
    _tlist = IF_TUP.get(isinstance(_arg, tuple))(_arg)
    lst: List[Any] = []
    for _ in _tlist:
        if _[0] == _[1]:
            lst += [_[0]]
            continue
        lst += list(range(_[0], _[1] + 1))
    return lst


#_3DA = '{num:03d}'


class Utils:
    """Utils Class supports routines to operate on multiple commands.

    These routines include:
    1) recall all command names
    2) recall all redeffinitions
    3) recall all macro deffintions
    4) reset all command names
    5) Process loop to select the above

    """

    _cmds: List[str] = ["cmds: -acr", "-rmn", "-ran", "-rmd", "-cacn", "-q"]
    _parser = argparse.ArgumentParser()
    _parser.add_argument(
        '-rmn', '--recall_macro_names',
        help='return all macro names',
        action="store_true")
    _parser.add_argument(
        '-ran', '--recall_all_names',
        help='return all renamed commands',
        action="store_true")
    _parser.add_argument(
        '-rmd', '--recall_macro_def',
        help='return all macro deffinitions',
        action="store_true")
    _parser.add_argument(
        '-cacn', '--reset_all_comd_names',
        help='reset all command names',
        action="store_true")
    _parser.add_argument(
        '-acr', '--apply_command_to_range',
        help='apply command to aruments in specified range',
        action="store_true")
    _parser.add_argument(
        '-q', '--quit',
        help='quit the util',
        action="store_true")

    def __init__(self, _uii: UserInput, _c: Controller, testing: bool = False, showhelp: bool = True):
        """__init__(ui,testing=False, showhelp=True)

        uii is the current UserInput
        c is the Controller
        testing True -> stops commands from being sent to the controller,
        and instead just prints them.
        showhelp True -> prints the help message
        """
        self._ui: UserInput = _uii
        self.s_port = _uii.serial_port
        self.cont_info = self.s_port.controller_info
        self.testing: bool = testing
        self.c: Controller = _c
        self.args = None
        if showhelp:
            Utils._parser.print_help()

    def __str__(self) -> str:
        return ", ".join(['testing:' + str(self.testing)] + Utils._cmds).rstrip()

    def __repr__(self) -> str:
        return ", ".join(['testing:' + str(self.testing)] + Utils._cmds).rstrip()

    def process_loop(self):
        """ProcessLoop()

        Select and execut which UTIL program to run.
        Your commands are run in the following order (assuming all are selected):
        0)-acr --apply_command_to_range
        1)-ran --recall_all_names
        2)-rmd --recall_macro_def
        3)-rmn  --recall_macro_names
        4)-cacn --reset_all_comd_names
        5)-quit

        This is the primary user access to the utilities
        """
        print('commands- one of: (-h|-acr|-rmn|-ran|-rmd|-cacn|-q)\n \
            Select and execut which UTIL program to run.\n \
            Your commands are run in the following order (assuming all are selected):\n \
                0)-acr --apply_command_to_range\n \
                1)-ran --recall_all_names\n \
                2)-rmd --recall_macro_def\n \
                3)-rmn  --recall_macro_names\n \
                4)-cacn --reset_all_comd_names\n \
                5)-quit')

        while True:
            instr = ""
            if self.testing:
                instr = "   -q -acr -rmn -ran -rmd -cacn"
            else:
                instr = input('select command>')

            options = instr.split()
            try:
                self.args = Utils._parser.parse_args(options)
                _bol_fun_tuple_tuple = (
                    (self.args.apply_command_to_range, self.doacr),
                    (self.args.recall_all_names, self.recall_all_names),
                    (self.args.recall_macro_def, self.recall_macro_deffinitions),
                    (self.args.recall_macro_names, self.recall_macro_names),
                    (self.args.reset_all_comd_names, self.reset_cmd_names),
                )
                # print(self.args)
                print("Command Complete")
            except SystemExit:
                pass
            else:
                for _ in _bol_fun_tuple_tuple:
                    if _[0]:
                        _[1]()
                if self.args.quit:
                    break

    def _get_cmd_names(self, rng):
        """_getCmdNames(rng)

        rng is the range of the commands to be scanned.

        sends a N011 cmdid for each cmdid in rng.
        If the cmdid has been renamed, logs the rename and the cmdid

        """
        def _sit(_a) -> bool:
            """_sit(a)

            checks if the response to the command indicates a rename

            """

            _px = self._ui.controller_type.rename_pat.search(_a)
            result: bool = False

            def _aa(_a):
                _g1 = _a.group(1)
                _g2 = _a.group(2)
                return _g1 == _g2

            def _rf(_a):
                return False

            if_px = {True: _aa, False: _rf, }
            result = if_px.get(_px)
            return result

        for i in rng:
            cmd = f'{i:03d}'
            if self.testing:
                print(
                    f'sending {self.cont_info.newcmd_dict.get("rcn")[0]}{cmd}')
                # .format(self.cont_info.newcmd_dict.get('rcn')[0], cmd))
                continue

            if self.c.sendcmd(
                self.cont_info.newcmd_dict.get('rcn')[0] + cmd,
                display=True,
                log_it=True,
                select_it=lambda a: not _sit(a)): sys.stdout.write('.')
            else:
                sys.stdout.write('-')

    def recall_macro_names(self):
        """recall_macro_names()

        Scans the user macros to get the macro names.

        """
        if self.cont_info.newcmd_dict.get('rcn')[0]:
            self._get_cmd_names(self.cont_info.userMacrosR)

    def doacr(self):
        """doacr()

        Apply command to range.

        Asks for a specified command to be applied to a range of single arguments
        for example in a deluxe 2 controller, you can specify cmd 062 (change
        the beginning of Command Names) input of "n062 1 30" will strip off
        extra digits to make commands 1-30 be three digits or less

        User input is at least 3 elements seperated by spaces (one space only?)
        max is 4 to allow a single argument to be applied to each of the things
        in the range.  Thus, input of "062 0 999 #" will rename all the commands of
        the controller to start with a #


        """
        # pylint: disable=R0912
        # pylint: disable=R0915
        print('Entering apply_command_to_range module')
        #notcmdttup = self.contInfo.newcmd_dict.get('notcmd')
        notcmdlst = _range_2_list(self.cont_info.newcmd_dict.get('notcmd'))
        _ = self.cont_info.newcmd_dict.get('ecn')
        if _:
            # do not apply to execute command by number command
            notcmdlst.append(_)
        lstcmd = self.cont_info.newcmd_dict.get('lstcmd')
        #dtmfpat = self.cont_info.newcmd_dict.get('dtmf')
        testargs = ['n123 456 458', 'N123 456 458',
                    '123 456 458', '123 456 458 a2#*0']

        testidx = 0
        while testidx < len(testargs):
            if self.testing:
                _ = testargs[testidx]
                testidx += 1
            else:
                _ = input(
                    f'specify the command and range of argument '
                    '(for example, 003 {str(lstcmd - 50)} {str(lstcmd)}) cr to exit >')
                # .format(str(lstcmd - 50), str(lstcmd)))

            if not _.strip():
                print("exiting apply_command_to_range module")
                break
            args = _.split(' ')
            if len(args) not in (3, 4):
                continue
            _ = args[0][0:1].upper()
            leadingn = _ == 'N'
            cmdnum = 0

            cmdnum = IF_N.get(leadingn)(args[0])
            startend = (int(args[1]), int(args[2]),
                        range(int(args[1]), int(args[2])))
            pram = ''
            if len(args) == 4:
                pram = args[3]
                if not self.cont_info.newcmd_dict.get('dtmf').match(pram):
                    # .format(pram))
                    print(f'{pram} must be only DTMF characters')
                    continue

            _ = (
                cmdnum < 0, startend[0] < 0,
                startend[1] < 0,
                cmdnum > lstcmd,
                startend[0] > startend[1],
                startend[1] > lstcmd
            )
            tst = False
            for _t in _:
                if _t:
                    tst = True
                    break

            if tst:
                continue

            _ = []
            if leadingn:
                _.append('N')
            # _.append(_3D.format(num=cmdnum))
            _.append(f'{cmdnum:03d}')
            cmd = "".join(_)
            for _ in startend[2]:
                if _ in notcmdlst:
                    continue
                command = " ".join([cmd, f'{_:03d}', pram])
                if self.testing:
                    print(f'sending {command}')  # .format(command))
                    continue
                if self.c.sendcmd(command, display=True, log_it=True):
                    sys.stdout.write('.')
                else:
                    print('Command error')
                    break  # break the for

    def recall_all_names(self):
        """recall_all_names()

        scans all cmdids, if the cmdid has been renamed, the rename and cmdid are logged

        """
        if self.cont_info.newcmd_dict.get('rcn')[0]:
            self._get_cmd_names(self.cont_info.commandsR)

    def reset_cmd_names(self):
        """ reset_cmd_names()

        Sends a n010 cmdid cmdid to the repeater to reset the command names for each cmdid
        but not for the system macros.
        """
        if not self.cont_info.newcmd_dict.get('rpcmdn')[0]:
            print('Command not supported for this controller')
            return

        for i in self.cont_info.safe2reset_name:
            #cmd = _3D.format(num=i)
            cmd = f'{i:03d}'
            if self.testing:
                print('sending {0}{1}{1}'
                      .format(self.cont_info.newcmd_dict.get('rpcmdn')[0], cmd, ))
                continue
            if self.c.sendcmd('{0}{1}{1}'
                              .format(self.cont_info.newcmd_dict.get('rpcmdn')[0], cmd, ),
                              display=False):
                sys.stdout.write('.')

    def recall_macro_deffinitions(self):
        """recallMacroDeffinitions()

        Scans the user macros to get the macro deffinitions.  If the deffinition has
        0 commands, the entry is not logged
        to the execution log.  Thus, you get a list of all the macros that are
        defined and what those deffinitions are in
        the execution log.

        """
        def _sit(_a: str) -> bool:
            """_sit(a)

            tests if the response is a macro deffinition
            """
            return not self._ui.controller_type.macro_def_pat.match(_a) is None

        valid = isinstance(self.cont_info.newcmd_dict.get('umacro'), tuple)
        if not (self.cont_info.newcmd_dict.get('rmc')[0] or valid):
            print('Command not supported for this controller')
            return False

        for i in self.cont_info.userMacrosR:
            #_ = _3D.format(num=i)
            _ = f'{i:03d}'
            if self.testing:
                print(
                    'sending {self.cont_info.newcmd_dict.get("rmc")[0]}{_}')
                # .format(self.cont_info.newcmd_dict.get('rmc')[0], _))
                continue
            if self.c.sendcmd(
                self.cont_info.newcmd_dict.get('rmc')[0] + _,
                display=False,
                log_it=True,
                select_it=lambda a: _sit(a),
                format_it=lambda a: self.cont_info.fmtRCM(a)
            ):
                sys.stdout.write('.')
        return True


if __name__ == '__main__':
    pass
