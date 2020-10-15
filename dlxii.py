#!/usr/bin/env python3
"""dlxii.py

A subclass of controllerspecific with deffinitions for the Club Deluxe II repeater

"""
import re
from typing import Any, Union, Tuple, Callable, TypeVar, Generic, Sequence, Mapping, List, Dict, Set, Deque, Iterable
import logging
import logging.handlers
import controllerspecific

LOGGER = logging.getLogger(__name__)


def _fmt_cmd(_arg) -> str:
    """_fmt_cmd(_arg)

    _arg is something that can be joined.

    Used in the newcmd_dict data structure
    """
    cmd: str = "".join(_arg)
    return cmd


def _fmt_proc(_mx):
    """_fmt_proc(_mx)

    _mx is a matcher that has been searched
    returns None if mx was not matched, and a groupdict if it was matched

    Used in the newcmd_dict data structure
    """
    if not _mx:
        return {}
    return _mx.groupdict()


def _fmt_proc_one(_mx):
    """_fmt_proc_one(_mx)

    _mx is a matcher that has been searched
    returns None if mx was not matched, and a groupdict if it was matched
    """
    if not _mx:
        return{}
    result = _mx.groupdict()
    cmds = _mx.group('cmds').strip()
    lst = [l for l in cmds.split('\n') if l.strip()]
    result['cmds'] = lst
    return result


def _fmt_n011(_str: str) -> Dict[str, Any]:
    """_fmtN011(s)

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


def _fmt_n054(_str: str) -> Dict[str, Any]:  # fmt macro contents
    """__fmtN054(s)

    runs a regex on string s. If unsuccessful, return an empty dict.
    if successfull, returns a dict with the following keys:
    'macro', 'numins', 'cmds' and 'full'

    """
    _mx = Device.N054Fmt_pat.search(_str)
    if _mx:
        cmds = _mx.group(3).strip()
        lst = [l for l in cmds.split('\n') if l.strip()]
        result: Dict[str, Any] = {"macro": _mx.group(1),
                                  "numins": _mx.group(2),
                                  "cmds": lst,
                                  "full": _mx.group(4),
                                  }
        return result
    return {}


class Device(controllerspecific.ControllerSpecific):
    """Device

    Subclass of ControllerSpecific
    Defines the RLC-CLUB Deluxe II v2.15 parameters
    """

    get_Ctr_type = 'RLC-Club Deluxe II v2.15'

    rename_pat = re.compile(
        r"Command number\s+(\d\d\d)\s+is\s+named\s+([0-9a-z]+)\..*",
        re.IGNORECASE | re.MULTILINE | re.DOTALL)

    macro_def_pat = re.compile(
        r".*contains\s+[1-9]([0-9]+)?\s+commands.*",
        re.MULTILINE | re.IGNORECASE | re.DOTALL)

    N054Fmt_pat = re.compile(
        r"MACRO\s+(?P<macro>\d{3,3})\s+contains\s+(?P<numins>\d{1,})\s+"
        + r"commands:(?P<cmds>.*)this.*(?P<full>\d{1,3}).*full\nOK\nOK\n",
        re.MULTILINE | re.IGNORECASE | re.DOTALL)

    N011Fmt_pat = re.compile(
        r'Command number\s*(?P<cmdno>\d{3,3})\s* is named ' +
        r'(?P<name>.*?)\.\s+It takes (?P<digs>\d{1,3}) digits of data\.',
        re.MULTILINE | re.IGNORECASE | re.DOTALL)

    def __init__(self):
        """__init__()


        """
        super().__init__()

        _sm = self.systemMacrosR
        self.safe2reset_name = [
            i for i in self.commandsR if i < _sm.start or i >= _sm.stop]

        _n029_pat = re.compile(
            r'This\s+is\s+(?P<A>\w+),\s*(?P<m>\d\d)-(?P<d>\d\d)-(?P<Y>\d{4,4})\s*\nOK\n',
            re.MULTILINE | re.IGNORECASE | re.DOTALL)

        _n027_pat = re.compile(
            r'The\s+time\s+is\s+(?P<I>\d{1,2}):(?P<M>\d\d)\s*(?P<p>[ap].m.)\nOK\n',
            re.MULTILINE | re.IGNORECASE | re.DOTALL)

        self.newcmd_dict.update(
            {'rpcmdn': ('N010', ),
             'rcn': ('N011', Device.N011Fmt_pat, _fmt_proc, None, ),
             'rmc': ('N054', Device.N054Fmt_pat, _fmt_proc_one, None, ),
             'gdate': ('N029', _n029_pat, _fmt_proc, None,),
             'gtime': ('N027', _n027_pat, _fmt_proc, None, ),
             'sdate': ('N028', None, None, _fmt_cmd, ),
             'stime': ('N025', None, None, _fmt_cmd, ),
             'smacro': (200, 499),
             'umacro': (500, 999),
             'lstcmd': 999,
             'notcmd': [(14, 19), (33, 33), (89, 89), (97, 99), (117, 118),
                        (153, 154), (168, 168), (193, 194), ],
             'ecn': 80,  # execute command by number
             'prompt': 'DTMF>',
             }  # cmd name:(cmd,replypat,replyfmt, cmdformat)
        )

        # the following three should be deprecated <<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>
        self.commandsR = range(0, self.newcmd_dict.get('lstcmd') + 1)
        self.userMacrosR = range(self.newcmd_dict.get('umacro')[0],
                                 self.newcmd_dict.get('umacro')[1] + 1)  # goes from 500 to 999
        self.systemMacrosR = range(self.newcmd_dict.get('smacro')[0],
                                   self.newcmd_dict.get('smacro')[1] + 1)  # goes from 200 to 499

    # def __fmtN011(self, _str):
        # """__fmtN011(s)

        # Performs a regex, and if successful, returns a dict with keys:
        # 'cmdno', 'name', and 'digs'
        # If unsuccssful, returns an empty dict.

        # """
        #_mx = Device.N011Fmt_pat.search(_str)
        # if _mx:
        # result = {'cmdno': _mx.group(1),
        # 'name': _mx.group(2),
        # 'digs': _mx.group(3),
        # }
        # return result
        # return {}

    def fmtRMC(self, _str: str) -> Tuple[str, Dict[str, Any]]:
        """fmtRMC(_str)

        Receives _str as a string and extracts the macro number, the number of instructions
        the commands, and percentage full.

        Recreates s from the extracted info and returns the recreated _str, as well as the
        dict of the relevent info.  The dict keys are: "macro", "numins", "cmds", and "full"

        If unable to parse the input _str, just returns the input _str and empty dict.
        """
        result: Tuple[str, Dict[str, Any]] = (_str, {})
        _d = _fmt_n054(_str)

        if _d:
            if _d.get("numins") != "0":
                _jj = ["Macro ", _d.get("macro"), " contains ",
                       _d.get("numins"), " commands\n", ]
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

    def fmtRCM(self, _str: str) -> Tuple[str, Dict[str, Any]]:
        """fmtRCM(_str)

        Formats the response from the Recall Command Name (N011) command
        _str is a string that includes the reponse

        Returns a tuple with the formatted string and a dictionary for the relevent info

        """
        result: Tuple[str, Dict[str, Any]] = (_str, {})
        _d: Dict[str, Any] = _fmt_n011(_str)
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
