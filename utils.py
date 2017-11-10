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
                         help = 'return all macro names',action ="store_true")
    _parser.add_argument('-ran', '--recall_all_names',
                         help = 'return all renamed commands', action="store_true")
    _parser.add_argument('-rmd', '--recall_macro_def',
                         help = 'return all macro deffinitions', action="store_true")
    _parser.add_argument('-cacn', '--reset_all_comd_names',
                         help = 'reset all command names', action="store_true")
    _parser.add_argument('-q', '--quit',
                         help = 'quit the util', action="store_true")


    def __init__(self, ui, testing=False, showhelp=True):
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
        if showhelp:
            try:
                self.args = Utils._parser.parse_args(['-h'])
            except SystemExit: pass


    def __str__(self):
        return  ", ".join(['testing:' + str(self.testing) ] + Utils._cmds).rstrip()

    def process_loop(self):
        """ProcessLoop()

        Select and execut which UTIL program to run.
        You commands are run in the following order (assuming all are selected):
        1)-ran
        2)-rmd
        3)-rmn
        4)-cacn
        5)-quit

        This is the primary user access to the utilities
        """
        print('commands- one of: (-h|-rmn|-ran|-rmd|-cacn|-q)')

        while True:
            instr = ""
            if self.testing:
                instr = "   -q -rmn -ran -rmd -cacn"
            else: instr = input('select command>')

            options= instr.split()

            try:
                self.args = Utils._parser.parse_args(options)
                print(self.args)
            except SystemExit:
                pass
            else:
                if self.args.recall_all_names:
                    self.recallAllNames()
                if self.args.recall_macro_def:
                    self.recallMacroDeffinitions()
                if self.args.recall_macro_names:
                    self.recallMacroNames()
                if self.args.reset_all_comd_names:
                    self.resetCmdNames()
                if self.args.quit:
                    break


    def _getCmdNames(self, rng):
        """_getCmdNames(rng)

        rng is the range of the commands to be scanned.

        sends a N011 cmdid for each cmdid in rng.
        If the cmdid has been renamed, logs the rename and the cmdid

        """
        def __sIt(a):
            """__sIt(a)

            checks if the response to the command indicates a rename

            """

            _px = self.ui.controller_type.rename_pat.search(a)
            result = False
            if px:
                _g1 = px.group(1)
                _g2 = px.group(2)
                result = _g1 == _g2
            else:
                result = False
            return result

        for i in rng:
            cmd = '{num:03d}'. format(num=i)
            if self.testing:
                print('sending %s%s' %(self.contInfo.cmdDict.get('rcn'), cmd ))
                continue

            if c.sendcmd(
                self.contInfo.cmdDict.get('rcn') + cmd,
                display=False,
                log_it=True,
                select_it=lambda a: not __sIt(a)): print('.', end='')
            else: print('-', end='')


    def recallMacroNames(self):
        """recallMacroNames()

        Scans the user macros to get the macro names.

       """
        self._getCmdNames(self.contInfo.userMacrosR)

    def recallAllNames(self):
        """recallAllNames()

        scans all cmdids, if the cmdid has been renamed, the rename and cmdid are logged

        """
        self._getCmdNames(self.contInfo.commandsR)


    def resetCmdNames(self):
        """ resetCmdNames()

        Sends a n010 cmdid cmdid to the repeater to reset the command names for each cmdid
        but not for the system macros.
        """

        for i in self.contInfo.safe2resetName:
            cmd = '{num:03d}'.format(num=i)
            if self.testing:
                print('sending %s%s%s' %(self.contInfo.cmdDict.get('rpcmdn'), cmd, cmd) )
                continue
            if c.sendcmd(self.contInfo.cmdDict.get('rpcmdn') + cmd + cmd, display = False):
                print('.', end='')

    def recallMacroDeffinitions(self):
        """recallMacroDeffinitions()

        Scans the user macros to get the macro deffinitions.  If the deffinition has
         0 commands, the entry is not logged
        to the execution log.  Thus, you get a list of all the macros that are
        defined and what those deffinitions are in
        the execution log.

        """
        def __sIt(_a):
            """__sIt(a)

            tests if the response is a macro deffinition
            """
            #pat = re.compile(
                #".*contains\s+[1-9]([0-9]+)?\s+commands.*",
                #re.MULTILINE | re.IGNORECASE | re.DOTALL)
            #if None == Utils._macro_def_pat.match(text):
            if Utils.ui.controller_type.macro_def_pat.match(_a) is None:
                return False

            return True

        for i in self.contInfo.userMacrosR:
            _ = '{num:03d}'.format(num=i)
            if self.testing:
                print('sending %s%s' %(self.contInfo.cmdDict.get('rmc'), _ ))
                continue
            if c.sendcmd(self.contInfo.cmdDict.get('rmc') + _,
                         display=False,
                         log_it=True,
                         select_it = lambda a: __sIt(_a),
                         format_it = lambda a: self.contInfo.fmtRCM(_a)):
                print('.', end='')


if __name__ == '__main__':
    pass
