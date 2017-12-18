#!/usr/bin/env python3
""" TBD """
import argparse

class Utils:
    """Utils Class supports routines to operate on multiple commands.

    These routines include:
    1) recall all command names
    2) recall all redeffinitions
    3) recall all macro deffintions
    4) reset all command names
    5) Process loop to select the above

    """
    _cmds = ["cmds: -rmn", "-ran", "-rmd", "-cacn", "-q"]
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
    _parser.add_argument('-acr', '--apply command to range',
                         help='apply command to aruments in specified range',
                         action="store_true")
    _parser.add_argument('-q', '--quit',
                         help='quit the util',
                         action="store_true")


    def __init__(self, ui, _c, testing=False, showhelp=True):
        """__init__(ui,testing=False, showhelp=True)

        ui is the current UserInput
        testing True -> stops commands from being sent to the controller,
        and instead just prints them.
        showhelp True -> prints the help message
        """
        self.ui = ui
        self.sp = ui.serial_port
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
                    (self.args.recall_apply_command_to_range, self.doacr),
                    (self.args.recall_all_names, self.recallAllNames),
                    (self.args.recall_macro_def, self.recallMacroDeffinitions),
                    (self.args.recall_macro_names, self.recallMacroNames),
                    (self.args.reset_all_comd_names, self.resetCmdNames),
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
            if _px:
                _g1 = _px.group(1)
                _g2 = _px.group(2)
                result = _g1 == _g2
            else:
                result = False
            return result

        for i in rng:
            cmd = '{num:03d}'. format(num=i)
            if self.testing:
                print('sending %s%s' %(self.contInfo.cmdDict.get('rcn'), cmd))
                continue

            if self.c.sendcmd(
                self.contInfo.cmdDict.get('rcn') + cmd,
                display=False,
                log_it=True,
                select_it=lambda a: not _sit(a)): print('.', end='')
            else: print('-', end='')


    def recallMacroNames(self):
        """recallMacroNames()

        Scans the user macros to get the macro names.

       """
        if self.contInfo.cmdDict.get('rcn'):
            self._get_cmd_names(self.contInfo.userMacrosR)

    def doacr(self):
        while True:
            userinput = input('specify the command and range of argument (for example, 003 500 1000)>')
            if not userinput.strip():
                break
            args = userinput.split(' ')
            if len(args) != 3:
                continue
            cmd = int(args[0])
            start = int(args[1])
            end = int(args[2])
            if cmd > 999 or start > end or end > 999:
                continue
            for i in range(start, end):
                '{num:03d}'.format(num=i)
                command = " ".join(['cmd', ])
                self.c.sendcmd()
        pass

    def recallAllNames(self):
        """recallAllNames()

        scans all cmdids, if the cmdid has been renamed, the rename and cmdid are logged

        """
        if self.contInfo.cmdDict.get('rcn'):
            self._get_cmd_names(self.contInfo.commandsR)


    def resetCmdNames(self):
        """ resetCmdNames()

        Sends a n010 cmdid cmdid to the repeater to reset the command names for each cmdid
        but not for the system macros.
        """
        if not self.contInfo.cmdDict.get('rpcmdn'):
            print('Command not supported for this controller')
            return
        for i in self.contInfo.safe2resetName:
            cmd = '{num:03d}'.format(num=i)
            if self.testing:
                print('sending %s%s%s' %(self.contInfo.cmdDict.get('rpcmdn'), cmd, cmd))
                continue
            if self.c.sendcmd(self.contInfo.cmdDict.get('rpcmdn') + cmd + cmd, display=False):
                print('.', end='')

    def recallMacroDeffinitions(self):
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
            #pat = re.compile(
                #".*contains\s+[1-9]([0-9]+)?\s+commands.*",
                #re.MULTILINE | re.IGNORECASE | re.DOTALL)
            #if None == Utils._macro_def_pat.match(text):
            #if self.ui.controller_type.macro_def_pat.match(_a) is None:
                #return False

            #return True
            return not self.ui.controller_type.macro_def_pat.match(_a) is None

        if not self.contInfo.cmdDict.get('rmc'):
            print('Command not supported for this controller')
            return

        for i in self.contInfo.userMacrosR:
            _ = '{num:03d}'.format(num=i)
            if self.testing:
                print('sending %s%s' %(self.contInfo.cmdDict.get('rmc'), _))
                continue
            if self.c.sendcmd(self.contInfo.cmdDict.get('rmc') + _,
                              display=False,
                              log_it=True,
                              select_it=lambda a: _sit(a),
                              format_it=lambda a: self.contInfo.fmtRCM(a)):
                print('.', end='')


if __name__ == '__main__':
    pass
