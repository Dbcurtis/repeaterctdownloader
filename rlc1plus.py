#!/usr/bin/env python3
""" to be done
"""
import re
import controllerspecific
class Rlc1Plus(controllerspecific.ControllerSpecific):
    """ to be done """

    def __init__(self):
        super().__init__()
        self.commandsR = range(0, 1000)
        self.userMacrosR = range(500, 1000)  # goes from 500 to 999
        self.systemMacrosR = range(200, 500)
        _sm = self.systemMacrosR
        self.safe2resetName = [i for i in self.commandsR if i < _sm.start or i >= _sm.stop]

        self.rename_pat = re.compile(
            r"Command number\s+(\d\d\d)\s+is\s+named\s+([0-9a-z]+)\..*",
            re.IGNORECASE | re.MULTILINE | re.DOTALL)

        self.macro_def_pat = re.compile(
            r".*contains\s+[1-9]([0-9]+)?\s+commands.*",
            re.MULTILINE | re.IGNORECASE | re.DOTALL)

        self.N054Fmt_pat = re.compile(
            r"MACRO\s+(\d{3,3})\s+contains\s+(\d{1,})\s+" + \
            r"commands:(.*)this.*(\d{1,3}).*full\nOK\nOK\n",
            re.MULTILINE | re.IGNORECASE | re.DOTALL)

        self.N011Fmt_pat = re.compile(
            r'Command number\s*(\d{3,3})\s* is named (.*?)\.\s+It takes (\d{1,3}) digits of data\.',
            re.MULTILINE | re.IGNORECASE | re.DOTALL)


        self.cmdDict = {'rpcmdn': 'N010', 'rcn': 'N011', 'rmc': 'N054',}
        """cmdDict

        A dict that associates commands with the controller specific command digits.
        """

        self.get_Ctr_type = lambda: 'RLC-Club Deluxe II v2.15'

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
        return '[Dlxii: rename:%s, macrodef:%s]' %  (self.rename_pat.pattern, \
               self.macro_def_pat.pattern)