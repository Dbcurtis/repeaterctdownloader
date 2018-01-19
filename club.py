#!/usr/bin/env python3
""" to be done
"""
import re
import controllerspecific

class Device(controllerspecific.ControllerSpecific):
    """ to be done """

    rename_pat = re.compile(
        r"Command number\s+(\d\d\d)\s+is\s+named\s+([0-9a-z]+)\..*",
        re.IGNORECASE | re.MULTILINE | re.DOTALL)

    macro_def_pat = re.compile(
        r".*contains\s+[1-9]([0-9]+)?\s+commands.*",
        re.MULTILINE | re.IGNORECASE | re.DOTALL)

    N054Fmt_pat = re.compile(
        r"MACRO\s+(?P<macro>\d{3,3})\s+contains\s+(?P<numins>\d{1,})\s+" + \
        r"commands:(?P<cmds>.*)this.*(?P<full>\d{1,3}).*full\nOK\nOK\n",
        re.MULTILINE | re.IGNORECASE | re.DOTALL)

    N011Fmt_pat = re.compile(
        r'Command number\s*(?P<cmdno>\d{3,3})\s*' + \
        r'is named (?P<name>.*?)\.\s+It takes (?P<digs>\d{1,3}) digits of data\.',
        re.MULTILINE | re.IGNORECASE | re.DOTALL)

    get_Ctr_type = 'RLC-Club v2.15'


    def __init__(self):
        super().__init__()
        self.commandsR = range(0, 1000)
        self.userMacrosR = range(500, 1000)  # goes from 500 to 999
        self.systemMacrosR = range(200, 500)
        _sm = self.systemMacrosR
        self.safe2resetName = [i for i in self.commandsR if i < _sm.start or i >= _sm.stop]


        __N029pat = re.compile(
            r'This\s+is\s+(?P<A>\w+),\s*(?P<m>\d\d)-(?P<d>\d\d)-(?P<Y>\d{4,4})\s*\nOK\n',
            re.MULTILINE | re.IGNORECASE | re.DOTALL)

        __N027pat = re.compile(
            r'The\s+time\s+is\s+(?P<I>\d{1,2}):(?P<M>\d\d)\s*(?P<p>[ap].m.)\nOK\n',
            re.MULTILINE | re.IGNORECASE | re.DOTALL)

        self.newcmd_dict = {'rpcmdn': ('N010', ),  #this dict is not used yet
                            'rcn': ('N011', Device.N011Fmt_pat, self.__fmt_proc, None, ),
                            'rmc': ('N054', Device.N054Fmt_pat, self.__fmt_proc_one, None, ),
                            'gdate': ('N029', __N029pat, self.__fmt_proc, None,),
                            'gtime': ('N027', __N027pat, self.__fmt_proc, None, ),
                            'sdate': ('N028', None, None, self.__fmt_cmd, ),
                            'stime': ('N025', None, None, self.__fmt_cmd, ),
                            'smacro': (200, 399),
                            'umacro': (400, 999),
                            'lstcmd': 999,
                            'notcmd': [(14, 19), (33, 33), (89, 89), (97, 99), (117, 118),
                                       (140, 140), (153, 154), (168, 168), (193, 194), ],
                            'prompt': 'DTMF>',
                           }  # cmd name:(cmd,replypat,replyfmt, cmdformat)
        """newcmd_dict

        a dict that assocates commands, reply patterns, and reply formatters
        """
    def __fmt_cmd(self, _arg):
        cmd = "".join(_arg)
        return cmd


    def __fmt_proc(self, _mx):
        if not _mx:
            return {}
        return _mx.groupdict()

    def __fmt_proc_one(self, _mx):
        if not _mx:
            return{}
        result = _mx.groupdict()
        cmds = _mx.group('cmds').strip()
        lst = [l for l in cmds.split('\n') if l.strip()]
        result['cmds'] = lst
        return result

    def __fmtN054(self, _str):  #fmt macro contents
        """__fmtN054(s)

        runs a regex on string s. If unsuccessful, return an empty dict.
        if successfull, returns a dict with the following keys:
        'macro', 'numins', 'cmds' and 'full'

        """
        _mx = Device.N054Fmt_pat.search(_str)
        if _mx:
            cmds = _mx.group(3).strip()
            lst = [l for l in cmds.split('\n') if l.strip()]
            result = {"macro": _mx.group(1),
                      "numins": _mx.group(2),
                      "cmds": lst,
                      "full": _mx.group(4),
                     }
            return result
        return {}

    def __fmtN011(self, _str):
        """__fmtN011(s)

        Performs a regex, and if successful, returns a dict with keys:
        'cmdno', 'name', and 'digs'
        If unsuccssful, returns an empty dict.

        """
        _mx = Device.N011Fmt_pat.search(_str)
        if _mx:
            result = {'cmdno': _mx.group(1),
                      'name': _mx.group(2),
                      'digs': _mx.group(3),
                     }
            return result
        return {}

    def fmtRMC(self, _str):
        """fmtRMC(_str)

        Receives s as a string and extracts the macro number, the number of instructions
        the commands, and percentage full.

        Recreates s from the extracted info and returns the recreated s, as well as the
        dict of the relevent info.  The dict keys are: "macro", "numins", "cmds", and "full"

        If unable to parse the input s, just returns the input s and empty dict.
        """
        result = (_str, {})
        _d = self.__fmtN054(_str)

        if _d:
            if  _d.get("numins") != "0":
                _jj = ["Macro ", _d.get("macro"), " contains ", _d.get("numins"), " commands\n", ]
                for _l in _d.get("cmds"):
                    _jj.append(_l.strip())
                    _jj.append('\n')

                _jj.append("This macro is ")
                _jj.append(_d.get("full") + " percent full")
                #ss = "".join(_jj)
                result = ("".join(_jj), _d)
        else:
            result = (_str, _d)

        return result

    def fmtRCM(self, _str):
        """fmtRCM(_str)

        Formats the response from the Recall Command Name (N011) command
        _str is a string that includes the reponse

        Returns a tuple with the formatted string and a dictionary for the relevent info

        """
        result = (_str, {})
        _d = self.__fmtN011(_str)
        if _d:
            _ll = ['Command number']
            _ll.append(_d.get('cmdno'))
            _ll.append("is named")
            _ll.append(_d.get('name') + '.')
            _ll.append(" It takes")
            _ll.append(_d.get('digs'))
            _ll.append('digits of data.')
            result = (" ".join(_ll), _d)

        else:
            result = (_str, _d)

        return result

    def __str__(self):
        return Device.get_Ctr_type
