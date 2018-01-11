#!/usr/bin/env python3
""" TBD """
import argparse
def _range_2_list(_arg):
    if isinstance(_arg, tuple):
        _tlist = [_arg]
    else:
        _tlist = _arg
    lst = []
    for t in _tlist:
        if t[0] == t[1]:
            lst += [t[0]]
            continue
        lst += list(range(t[0], t[1]+1))
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
                    (self.args.apply_command_to_range, self.doacr),
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
            cmd = Utils._3d.format(num=i)
            if self.testing:
                print('sending {}{}'.format(self.contInfo.cmdDict.get('rcn'), cmd))
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
        print('Entering apply_command_to_range module')
        notcmdttup =  self.contInfo.newcmd_dict.get('notcmd')
        notcmdlst = _range_2_list(notcmdttup)                
        lstcmd = self.contInfo.newcmd_dict.get('lstcmd')
        testargs = ['n123 456 458', 'N123 456 458', "", ]
        testidx = 0
        while True:
            userinput = ''
            if self.testing:
                userinput = testargs[testidx]
                testidx += 1
            else:
                userinput = input('specify the command and range of argument (for example, 003 {} {}) cr to exit >'.format(str(lstcmd-50), str(lstcmd)))
            if not userinput.strip():
                print("exiting apply_command_to_range module")
                break
            args = userinput.split(' ')
            if len(args) != 3:
                continue
            cmdtxt = args[0]
            _1st = cmdtxt[0:1].upper()
            leadingn = _1st == 'N'
            cmdnum = 0
            if leadingn:
                cmdnum = int(args[0][1:])
            else:
                cmdnum = int(args[0])
            
            start = int(args[1])
            end = int(args[2])
            
            aa = (cmdnum < 0 , start < 0, end < 0, cmdnum > lstcmd, start > end ,  end > lstcmd)
            tst = False
            for t in aa:
                if t:
                    tst = True
                    break
            
            if tst:
                continue
                
            aa = []
            if leadingn:
                aa.append('N')
            aa.append(Utils._3d.format(num=cmdnum))
            cmd = "".join(aa)
            for i in range(start, end):
                if i in notcmdlst:
                    continue
                command = " ".join([cmd, Utils._3d.format(num=i)])
                if self.testing:
                    print('sending {}'.format(command))
                    continue
                if self.c.sendcmd(command, display=True, log_it=True):
                    print('.', end='')
                else:
                    print('Command error')
                    break #break the for
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
            cmd =Utils._3d.format(num=i)
            if self.testing:
                print('sending {}{}{}'.format(self.contInfo.cmdDict.get('rpcmdn'), cmd, cmd))
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

            return not self.ui.controller_type.macro_def_pat.match(_a) is None

        if not self.contInfo.cmdDict.get('rmc'):
            print('Command not supported for this controller')
            return

        for i in self.contInfo.userMacrosR:
            _ = Utils._3d.format(num=i)
            if self.testing:
                print('sending {}{}'.format(self.contInfo.cmdDict.get('rmc'), _))
                continue
            if self.c.sendcmd(self.contInfo.cmdDict.get('rmc') + _,
                              display=False,
                              log_it=True,
                              select_it=lambda a: _sit(a),
                              format_it=lambda a: self.contInfo.fmtRCM(a)):
                print('.', end='')


if __name__ == '__main__':
    pass
