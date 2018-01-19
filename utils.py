#!/usr/bin/env python3
""" TBD """
import argparse

IF_N = {True: lambda a: int(a[1:]), False: lambda a: int(a),}

def _range_2_list(_arg):
    if isinstance(_arg, tuple):
        _tlist = [_arg]
    else:
        _tlist = _arg
    lst = []
    for _ in _tlist:
        if _[0] == _[1]:
            lst += [_[0]]
            continue
        lst += list(range(_[0], _[1]+1))
    return lst

class Utils:
    """Utils Class supports routines to operate on multiple commands.

    These routines include:
    1) recall all command names
    2) recall all redeffinitions
    3) recall all macro deffintions
    4) reset all command names
    5) Process loop to select the above

    """
    _3d = '{num:03d}'
    _cmds = ["cmds: -acr", "-rmn", "-ran", "-rmd", "-cacn", "-q"]
    _parser = argparse.ArgumentParser()
    _parser.add_argument('-rmn', '--recall_macro_names',
                         help='return all macro names',
                         action="store_true")
    _parser.add_argument('-ran', '--recall_all_names',
                         help='return all renamed commands',
                         action="store_true")
    _parser.add_argument('-rmd', '--recall_macro_def',
                         help='return all macro deffinitions',
                         action="store_true")
    _parser.add_argument('-cacn', '--reset_all_comd_names',
                         help='reset all command names',
                         action="store_true")
    _parser.add_argument('-acr', '--apply_command_to_range',
                         help='apply command to aruments in specified range',
                         action="store_true")
    _parser.add_argument('-q', '--quit',
                         help='quit the util',
                         action="store_true")



    def __init__(self, _ui, _c, testing=False, showhelp=True):
        """__init__(ui,testing=False, showhelp=True)

        ui is the current UserInput
        testing True -> stops commands from being sent to the controller,
        and instead just prints them.
        showhelp True -> prints the help message
        """
        self.ui = _ui
        self.sp = _ui.serial_port
        self.contInfo = self.sp.controller_info
        self.testing = testing
        self.c = _c
        if showhelp:
            try:
                self.args = Utils._parser.parse_args(['-h'])
            except SystemExit:
                pass


    def __str__(self):
        return  ", ".join(['testing:' + str(self.testing)] + Utils._cmds).rstrip()

    def process_loop(self):
        """ProcessLoop()

        Select and execut which UTIL program to run.
        You commands are run in the following order (assuming all are selected):
        0)-acr
        1)-ran
        2)-rmd
        3)-rmn
        4)-cacn
        5)-quit

        This is the primary user access to the utilities
        """
        print('commands- one of: (-h|-acr|-rmn|-ran|-rmd|-cacn|-q)')

        while 1:
            instr = ""
            if self.testing:
                instr = "   -q -acr -rmn -ran -rmd -cacn"
            else: instr = input('select command>')

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
                #print(self.args)
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
        def _sit(_a):
            """_sit(a)

            checks if the response to the command indicates a rename

            """

            _px = self.ui.controller_type.rename_pat.search(_a)
            result = False
            def _aa(_a):
                _g1 = _a.group(1)
                _g2 = _a.group(2)
                return _g1 == _g2
            def _rf(_a):
                return False

            IF_PX = {True: _aa, False: _rf,}
            result = IF_PX.get(_px)
            #if _px:
                #_g1 = _px.group(1)
                #_g2 = _px.group(2)
                #result = _g1 == _g2
            #else:
                #result = False
            #assert result1 == result
            return result

        for i in rng:
            cmd = Utils._3d.format(num=i)
            if self.testing:
                print('sending {}{}'.format(self.contInfo.newcmd_dict.get('rcn')[0], cmd))
                continue

            if self.c.sendcmd(
                self.contInfo.newcmd_dict.get('rcn')[0] + cmd,
                display=False,
                log_it=True,
                select_it=lambda a: not _sit(a)): print('.', end='')
            else: print('-', end='')


    def recall_macro_names(self):
        """recall_macro_names()

        Scans the user macros to get the macro names.

       """
        if self.contInfo.newcmd_dict.get('rcn')[0]:
            self._get_cmd_names(self.contInfo.userMacrosR)

    def doacr(self):
        """doacr()

        """
        print('Entering apply_command_to_range module')
        #notcmdttup = self.contInfo.newcmd_dict.get('notcmd')
        notcmdlst = _range_2_list(self.contInfo.newcmd_dict.get('notcmd'))
        lstcmd = self.contInfo.newcmd_dict.get('lstcmd')
        testargs = ['n123 456 458', 'N123 456 458', "", ]
        testidx = 0
        while True:
            userinput = ''
            if self.testing:
                userinput = testargs[testidx]
                testidx += 1
            else:
                userinput = input(
                    'specify the command and range of argument (for example, 003 {} {}) cr to exit >'.format(str(lstcmd-50), str(lstcmd)))
            if not userinput.strip():
                print("exiting apply_command_to_range module")
                break
            args = userinput.split(' ')
            if len(args) != 3:
                continue
            #cmdtxt = args[0]
            _1st = args[0][0:1].upper()
            leadingn = _1st == 'N'
            cmdnum = 0

            cmdnum = IF_N.get(leadingn)(args[0])
            #if leadingn:
                #cmdnum = int(args[0][1:])
            #else:
                #cmdnum = int(args[0])

            start = int(args[1])
            end = int(args[2])

            _ = (cmdnum < 0, start < 0, end < 0, cmdnum > lstcmd, start > end, end > lstcmd)
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
            _.append(Utils._3d.format(num=cmdnum))
            cmd = "".join(_)
            for _i in range(start, end):
                if _i in notcmdlst:
                    continue
                command = " ".join([cmd, Utils._3d.format(num=_i)])
                if self.testing:
                    print('sending {}'.format(command))
                    continue
                if self.c.sendcmd(command, display=True, log_it=True):
                    print('.', end='')
                else:
                    print('Command error')
                    break #break the for

    def recall_all_names(self):
        """recall_all_names()

        scans all cmdids, if the cmdid has been renamed, the rename and cmdid are logged

        """
        if self.contInfo.newcmd_dict.get('rcn')[0]:
            self._get_cmd_names(self.contInfo.commandsR)


    def reset_cmd_names(self):
        """ reset_cmd_names()

        Sends a n010 cmdid cmdid to the repeater to reset the command names for each cmdid
        but not for the system macros.
        """
        if not self.contInfo.newcmd_dict.get('rpcmdn')[0]:
            print('Command not supported for this controller')
            return

        for i in self.contInfo.safe2resetName:
            cmd = Utils._3d.format(num=i)
            if self.testing:
                print('sending {}{}{}'.format(self.contInfo.newcmd_dict.get('rpcmdn')[0], cmd, cmd))
                continue
            if self.c.sendcmd(self.contInfo.newcmd_dict.get('rpcmdn')[0] + cmd + cmd, display=False):
                print('.', end='')

    def recall_macro_deffinitions(self):
        """recallMacroDeffinitions()

        Scans the user macros to get the macro deffinitions.  If the deffinition has
         0 commands, the entry is not logged
        to the execution log.  Thus, you get a list of all the macros that are
        defined and what those deffinitions are in
        the execution log.

        """
        def _sit(_a):
            """_sit(a)

            tests if the response is a macro deffinition
            """

            return not self.ui.controller_type.macro_def_pat.match(_a) is None

        if not self.contInfo.newcmd_dict.get('rmc')[0]:
            print('Command not supported for this controller')
            return

        for i in self.contInfo.userMacrosR:
            _ = Utils._3d.format(num=i)
            if self.testing:
                print('sending {}{}'.format(self.contInfo.newcmd_dict.get('rmc')[0], _))
                continue
            if self.c.sendcmd(self.contInfo.newcmd_dict.get('rmc')[0] + _,
                              display=False,
                              log_it=True,
                              select_it=lambda a: _sit(a),
                              format_it=lambda a: self.contInfo.fmtRCM(a)):
                print('.', end='')


if __name__ == '__main__':
    pass
