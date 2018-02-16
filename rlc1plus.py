#!/usr/bin/env python3
""" to be done
"""
import re
import controllerspecific



def _fmt_cmd(_arg):
    cmd = "".join(_arg)
    return cmd


def _fmt_proc(_mx):
    if not _mx:
        return {}
    return _mx.groupdict()

def _fmt_proc_one(_mx):
    if not _mx:
        return{}
    result = _mx.groupdict()
    cmds = _mx.group('cmds').strip()
    lst = [l for l in cmds.split('\n') if l.strip()]
    result['cmds'] = lst
    return result

class Device(controllerspecific.ControllerSpecific):
    """ to be done """


    rename_pat = re.compile(
        r"Command number\s+(\d\d\d)\s+is\s+named\s+([0-9a-z]+)\..*",
        re.IGNORECASE | re.MULTILINE | re.DOTALL)

    macro_def_pat = re.compile(
        r".*contains\s+[1-9]([0-9]+)?\s+commands.*",
        re.MULTILINE | re.IGNORECASE | re.DOTALL)

    N054Fmt_pat = re.compile(
        r"MACRO\s+(\d{3,3})\s+contains\s+(\d{1,})\s+" + \
        r"commands:(.*)this.*(\d{1,3}).*full\nOK\nOK\n",
        re.MULTILINE | re.IGNORECASE | re.DOTALL)

    N011Fmt_pat = re.compile(
        r'Command number\s*(\d{3,3})\s* is named (.*?)\.\s+It takes (\d{1,3}) digits of data\.',
        re.MULTILINE | re.IGNORECASE | re.DOTALL)

    get_Ctr_type = 'RLC1 Plus'

    def __init__(self):
        super().__init__()
        print(">>>>>>>>>>>>THIS NEEDS TO BE TESTED it is all "+\
              "wrong re formatting and possibly commands>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        self.commandsR = range(0, 215)
        self.userMacrosR = range(141, 210)  # goes from 141 to 210
        self.systemMacrosR = range(200, 500)
        _sm = self.systemMacrosR
        self.safe2reset_name = [i for i in self.commandsR if i < _sm.start or i >= _sm.stop]


        __N029pat = re.compile(
            r'This\s+is\s+(?P<A>\w+),\s*(?P<m>\d\d)-(?P<d>\d\d)-(?P<Y>\d{4,4})\s*\nOK\n',
            re.MULTILINE | re.IGNORECASE | re.DOTALL)

        __N027pat = re.compile(
            r'The\s+time\s+is\s+(?P<I>\d{1,2}):(?P<M>\d\d)\s*(?P<p>[ap].m.)\nOK\n',
            re.MULTILINE | re.IGNORECASE | re.DOTALL)

        self.newcmd_dict.update( # these are all wrong and will need to be changed
            {
                'rpcmdn': ('027', ),
                'rcn': ('028', Device.N011Fmt_pat, _fmt_proc, None, ),
                'rmc': ('129', Device.N054Fmt_pat, _fmt_proc_one, None, ),
                'gdate': ('056', __N029pat, _fmt_proc, None,),
                'gtime': ('054', __N027pat, _fmt_proc, None, ),
                'sdate': ('059', None, None, _fmt_cmd, ),
                'stime': ('058', None, None, _fmt_cmd, ),
                'umacro': (141, 210),
                'lstcmd': 215,
                'notcmd': [(14, 19), (33, 33), (89, 89), (97, 99), (117, 118),
                           (153, 154), (168, 168), (193, 194), ],
                'prompt': 'DTMF>',
                }  # cmd name:(cmd,replypat,replyfmt, cmdformat)
            )


    def __fmtN054(self, _str):  #fmt macro contents
        """__fmtN054(s)

        runs a regex on string s. If unsuccessful, return an empty dict.
        if successfull, returns a dict with the following keys:
        'macro', 'numins', 'cmds' and 'full'

        """
        _mx = self.N054Fmt_pat.search(_str)
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
        _mx = self.N011Fmt_pat.search(_str)
        if _mx:
            result = {'cmdno': _mx.group(1),
                      'name': _mx.group(2),
                      'digs': _mx.group(3),
                     }
            return result
        return {}

    def fmtRMC(self, _str):
        """fmtRMC(s)

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

    def fmtRCM(self, s):
        """fmtRCM(s)

        Formats the response from the N011 command
        s is a string that includes the reponse

        Returns a tuple with the formatted string and a dictionary for the relevent info

        """
        result = (s, {})
        _d = self.__fmtN011(s)
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
            result = (s, _d)

        return result

    def __str__(self):
        return Device.get_Ctr_type
