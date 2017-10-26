#!/usr/bin/env python3
import os
import sys
import re
import controllerspecific
class DlxII(controllerspecific.ControllerSpecific):
    
    def __init__(self):
        super().__init__()
        self.commandsR=range(0,1000)
        self.userMacrosR = range(500, 1000)  # goes from 500 to 999
        self.systemMacrosR = range(200, 500)
        sm =  self.systemMacrosR
        self.safe2resetName = [i for i in self.commandsR if i < sm.start or i >= sm.stop]        
        
        self.rename_pat = re.compile(
            "Command number\s+(\d\d\d)\s+is\s+named\s+([0-9a-z]+)\..*",
            re.IGNORECASE | re.MULTILINE | re.DOTALL)
        
        self.macro_def_pat = re.compile(
            ".*contains\s+[1-9]([0-9]+)?\s+commands.*",
            re.MULTILINE | re.IGNORECASE | re.DOTALL)
        
        self.N054Fmt_pat = re.compile(
            "MACRO\s+(\d{3,3})\s+contains\s+(\d{1,})\s+commands:(.*)this.*(\d{1,3}).*full\nOK\nOK\n", 
            re.MULTILINE | re.IGNORECASE | re.DOTALL)
        
        self.N011Fmt_pat = re.compile('Command number\s*(\d{3,3})\s* is named (.*?)\.\s+It takes (\d{1,3}) digits of data\.',
            re.MULTILINE | re.IGNORECASE | re.DOTALL)                       
        
        
        self.cmdDict = {'rpcmdn': 'N010', 'rcn': 'N011', 'rmc': 'N054',}
        """cmdDict
        
        A dict that associates commands with the controller specific command digits.
        """
        
        self.get_Ctr_type = lambda : 'RLC-Club Deluxe II v2.15'
    
    def __fmtN054(self, s):  #fmt macro contents
        """__fmtN054(s)
        
        runs a regex on string s. If unsuccessful, return an empty dict.
        if successfull, returns a dict with the following keys:
        'macro', 'numins', 'cmds' and 'full'
        
        """
        mx = self.N054Fmt_pat.search(s)
        if mx:
            cmds = mx.group(3).strip()
            lst = [l for l in cmds.split('\n') if len(l.strip()) > 0]
            result = {"macro": mx.group(1),
                      "numins": mx.group(2),
                      "cmds": lst,
                      "full": mx.group(4),
                      }
            return result
            
        else:
            return {}
        
    def __fmtN011(self, s):
        """__fmtN011(s)
        
        Performs a regex, and if successful, returns a dict with keys:
        'cmdno', 'name', and 'digs'
        If unsuccssful, returns an empty dict.
        
        """
        mx = self.N011Fmt_pat.search(s)
        if mx:
            cmds = mx.group(3).strip()
            lst = [l for l in cmds.split('\n') if len(l.strip()) > 0]
            result = {'cmdno': mx.group(1),
                      'name': mx.group(2),
                      'digs': mx.group(3), 
                      }
            return result
            
        else:
            return {}        
        
    def fmtRMC(self, s):
        """fmtRMC(s)
        
        Receives s as a string and extracts the macro number, the number of instructions
        the commands, and percentage full.
        
        Recreates s from the extracted info and returns the recreated s, as well as the
        dict of the relevent info.  The dict keys are: "macro", "numins", "cmds", and "full"
        
        If unable to parse the input s, just returns the input s and empty dict.
        """
        result = (s, {})
        d = self.__fmtN054(s)

        if d:
            if  (d.get("numins") != "0"):             
                jj = ["Macro ", d.get("macro"), " contains ", d.get("numins"), " commands\n", ]
                for l in d.get("cmds"):
                    jj.append(l.strip())
                    jj.append('\n')
                
                jj.append("This macro is ")
                jj.append(d.get("full") + " percent full")
                ss = "".join(jj)
                result = (ss, d)
        else:
            result = (s, d)
        
        return result
    
    def fmtRCM(self, s):
        """fmtRCM(s)
        
        Formats the response from the N011 command
        s is a string that includes the reponse
     
        Returns a tuple with the formatted string and a dictionary for the relevent info
        
        """
        result = (s, {})
        d = self.__fmtN011(s)
        if d:
            ll = ['Command number']
            ll.append(d.get('cmdno'))
            ll.append("is named")
            ll.append(d.get('name') + '.')
            ll.append(" It takes")
            ll.append(d.get('digs'))
            ll.append('digits of data.')
            result = (" ".join(ll), d)
            
        else:
            result = (s, d)
            
        return result
    
    def __str__(self):
        return '[Dlxii: rename:%s, macrodef:%s]' %  (self.rename_pat.pattern, 
               self.macro_def_pat.pattern)
    