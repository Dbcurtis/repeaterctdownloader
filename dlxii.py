#!/usr/bin/env python3
import os
import sys
import re
import controllerspecific
class DlxII(controllerspecific.ControllerSpecific):
    get_Ctr_type = lambda : 'RLC-Club Deluxe II v2.15'
    def __init__(self):
        super().__init__()
        self.commandsR=range(0,1000)
        self.userMacrosR = range(500, 1000)  # goes from 500 to 999
        self.rename_pat = re.compile(
            "Command number\s+(\d\d\d)\s+is\s+named\s+([0-9a-z]+)\..*",
            re.IGNORECASE | re.MULTILINE | re.DOTALL)
        self.macro_def_pat = re.compile(
            ".*contains\s+[1-9]([0-9]+)?\s+commands.*",
            re.MULTILINE | re.IGNORECASE | re.DOTALL)
        self.N054Fmt_pat = re.compile(
            "MACRO\s+(\d{3,3})\s+contains\s+(\d{1,})\s+commands:(.*)this.*(\d{1,3}).*full\nOK\nOK\n"
            ,re.MULTILINE | re.DOTALL| re.IGNORECASE 
        )
    
    def _fmt054(self, s):  #fmt macro contents
        mx = self.N054Fmt_pat.search(s)
        if mx:
            result = {"macro": mx.group(1),
                      "numins": mx.group(2),
                      "cmds": mx.group(3),
                      "full": mx.group(4),
                      }
            return result
            
        else:
            return {}
        
    def fmt054(self, s):
        result = (s, {})
        d = _fmt054(s)

        if d:
            if  (d.get("numins") != "0"):
                cmdl = d.get("cmds").split("\s*#")
                d.put("cmdlst", cmdl)               
                jj = ["Macro ", d.get("macro"), " contains ", d.get("numins"), "commands\n", ]
                jj.append(d.get("cmdlst"))
                jj.append("This macro is ")
                jj.append(d.get("full") + " percent full")
                ss = "".join(jj)
                result = (ss, d)
            pass
        else:
            result = (s, d)
        
        return result
            