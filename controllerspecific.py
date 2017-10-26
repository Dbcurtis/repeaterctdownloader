#!/usr/bin/env python3

import os
import sys
import re

class ControllerSpecific:
    
    class SerialSpeedinfo:
        def __init__(self,bps,cpsDelay):
            self.bps=0
            self.cpsDelay=0.0
            self.bps = bps
            self.cpsDelay = cpsDelay        
    
        def __str__(self):
            return '[CPS: %s]' % (str(int(self.bps / 10)) + ", " + str(self.cpsDelay))
    
        def __repr__(self):
            return '[CPS: %s]' % (str(int(self.bps / 10)) + ", " + str(self.cpsDelay))
        

    
    def __donothing(self, s):
        return {}
    
    def fmtRMC(self, s):
        return (s, self.__donothing(s))
    
    def fmtRCM(self, s):
        return (s, self.__donothing(s)) 
   
    get_Ctr_type = lambda: None
        
    def __init__(self):
        self.get_Ctr_type = lambda : 'Abstract Controller'
        self.userMacrosR = range(0, 0)  
        self.commandsR = range(0, 0)
        self.systemMacrosR = range(0, 0)
        sm =  self.systemMacrosR
        self.safe2resetName = [i for i in self.commandsR if i < sm.start or i > sm.stop]
        self.cpsData=[
           self.SerialSpeedinfo(9600, 0.2),
           self.SerialSpeedinfo(19200, 0.1),
           self.SerialSpeedinfo(4800, 0.4),
           self.SerialSpeedinfo(2400, 0.8),
           self.SerialSpeedinfo(1200, 1.6),
           self.SerialSpeedinfo(600, 3),
           self.SerialSpeedinfo(300, 6)
        ]
        self.cmdDict = {'rpcmdn': '', 'rcn': '', 'rmc': '',}
        for ssi in self.cpsData:
            #t =  0.1 + (1100.0 / ssi.bps)
            ssi.cpsDelay  = round(0.1 + (1100.0 / ssi.bps), 3)              
        
        self.rename_pat = re.compile(
            ".*",
            re.IGNORECASE | re.MULTILINE | re.DOTALL)
        
        self.macro_def_pat = re.compile(
            ".*",
            re.MULTILINE | re.IGNORECASE | re.DOTALL)
        
    def __str__(self):
        return '[ControllerSpecific: rename:%s, macrodef:%s]' %  (self.rename_pat.pattern, 
               self.macro_def_pat.pattern)
    
