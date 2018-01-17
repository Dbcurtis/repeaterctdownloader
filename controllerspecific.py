#!/usr/bin/env python3
"""  TBD  """

import re

#offsets into the newcmd_dict
INST = 0
PAT = 1
REPL_FMT = 2

class ControllerSpecific:
    """ControllerSpecific

    TBD
    """
    get_Ctr_type = 'Abstract Controller'


    
    class SerialSpeedinfo:
        """SerialSpeedinfo

        """
        def __init__(self, bps, cpsDelay):
            self.bps = 0
            self.cpsDelay = 0.0
            self.bps = bps
            self.cpsDelay = cpsDelay


        def __str__(self):
            return '[CPS: {}]'.format(str(int(self.bps / 10)) + ", " + str(self.cpsDelay))

        def __repr__(self):
            return '[CPS: {}]'.format(str(int(self.bps / 10)) + ", " + str(self.cpsDelay))


    def fmtRCM(self, _str):
        """fmtRCM(_str)

        Formats the response from the Recall Command Name command if such exists
        _str is a string that includes the response

        Returns a tuple with the formatted string and a dictionary for the relevent info

        """
        return (_str, {})


    def fmtRMC(self, _str):
        """fmtRMC(_str)

        Receives _str as a string and extracts the macro number, the number of instructions
        the commands, and percentage full.

        Recreates _str from the extracted info and returns the recreated _str, as well as the
        dict of the relevent info.  The dict keys are: "macro", "numins", "cmds", and "full"

        If unable to parse the input _str, just returns the input s and empty dict.
        """
        return (_str, {})


    def __init__(self):

        self.userMacrosR = range(0, 0)
        self.commandsR = range(0, 0)
        self.systemMacrosR = range(0, 0)
        _ = self.systemMacrosR
        self.safe2resetName = [i for i in self.commandsR if i < _.start or i > _.stop]
        self.cps_data = [
            self.SerialSpeedinfo(9600, 0.2),
            self.SerialSpeedinfo(19200, 0.1),
            self.SerialSpeedinfo(4800, 0.4),
            self.SerialSpeedinfo(2400, 0.8),
            self.SerialSpeedinfo(1200, 1.6),
            self.SerialSpeedinfo(600, 3),
            self.SerialSpeedinfo(300, 6)
        ]

        self.newcmd_dict = {'rpcmdn': (None, None, None, ),
                            'rcn': (None, None, None, ),
                            'rmc': (None, None, None, ),
                            'gdate': (None, None, None, ),
                            'gtime': (None, None, None, ),
                            'sdate': (None, None, None, ),
                            'stime': (None, None, None, ),
                            'smacro': None,
                            'umacro': None,
                            'lstcmd': None,
                            'notcmd': None,
                            'prompt': '\n',
                           }  # cmd name:(cmd,replypat,replyfmt, cmdformat)
        self.cmdDict = {'rpcmdn': None,
                        'rcn': None,
                        'rmc': None,
                        'prompt': '\n',
                       }
        for ssi in self.cps_data:
            ssi.cpsDelay = round(0.1 + (1100.0 / ssi.bps), 3)

        self.rename_pat = re.compile(
            ".*",
            re.IGNORECASE | re.MULTILINE | re.DOTALL)

        self.macro_def_pat = re.compile(
            ".*",
            re.MULTILINE | re.IGNORECASE | re.DOTALL)

    def __str__(self):
        return ControllerSpecific.get_Ctr_type
