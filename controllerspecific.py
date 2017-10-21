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
            return '[CPS: %s]' % (str(self.bps) + ", " + str(self.cpsDelay))
    
        def __repr__(self):
            return '[CPS: %s]' % (str(self.bps) + ", " + str(self.cpsDelay))
        
    self.rename_pat = re.compile(
        ".*",
        re.IGNORECASE | re.MULTILINE | re.DOTALL)
    
    self.macro_def_pat = re.compile(
        ".*",
        re.MULTILINE | re.IGNORECASE | re.DOTALL)
    
    def _fmt054(s):
        return {}
    
    def fmt054(s):
        return (s, _fmt054(s))
   
    get_Ctr_type = lambda: None
        
    def __init__(self):
        self.userMacrosR = range(0, 0)  
        self.commandsR = range(0, 0)
        self.cpsData=[
           self.SerialSpeedinfo(9600, 0.2),
           self.SerialSpeedinfo(19200, 0.1),
           self.SerialSpeedinfo(4800, 0.4),
           self.SerialSpeedinfo(2400, 0.8),
           self.SerialSpeedinfo(1200, 1.6),
           self.SerialSpeedinfo(600, 3),
           self.SerialSpeedinfo(300, 6)
        ]
     
        for cpsi in self.cpsData: cpsi.cpsDelay = self.cpsDelay + (1100.0/cpsi.bps)  # time for 110 characters
        
