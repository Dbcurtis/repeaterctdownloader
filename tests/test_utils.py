#!/usr/bin/env python3
"""
Test file for utils
"""
from __future__ import print_function
import os
import sys
import dlxii
import unittest
import serial
import myserial
import userinput
import utils
import getports


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

class Testutils(unittest.TestCase):
    sdevice = ""
    gsp = serial.Serial()
    
    def setUp(self):
        pass 
            
    def tearDown(self):
        pass           
    
    @classmethod
    def setUpClass(cls):
  
        devs = getports.GetPorts().get()
        if not devs:
            eprint("No serial ports exist.")
            raise SystemExit("no serial ports exist")        
        sp = serial.Serial()
        sp.baudrate= 1200
        sp.timeout=.5
        devs = getports.GetPorts().get()
        for dev in devs:
            sp.port=dev
            if not sp.isOpen():
                break
        
        Testutils.sdevice=sp.port
        assert (len(Testutils.sdevice)>0)           
        assert(not sp.isOpen())
        sp.open()    
        openresult= sp.isOpen()
        if sp.isOpen():sp.close()
        myserial.MySerial._debugging = True
        myserial.MySerial._debugreturns =  [b'ok\nDTMF>']
        myserial.MySerial._dbidx=0           
        assert(openresult)        
   
    @classmethod
    def tearDownClass(cls):
        sp = Testutils.gsp
        if sp.isOpen():sp.close()
        myserial.MySerial._debugging = False
        myserial.MySerial._debugreturns =  [b'ok\nDTMF>']
        myserial.MySerial._dbidx=0        

    def testcreation(self):
        ui = userinput.UserInput()
        ui.commPort = Testutils.sdevice
        utili = utils.Utils(ui, testing= False, showhelp = False)
        self.assertFalse(utili.testing)
        utili = utils.Utils(ui, testing= True, showhelp = False)
        self.assertTrue(utili.testing)
        pass

    def testprocessLoop(self):
        ui = userinput.UserInput()
        ui.commPort = Testutils.sdevice
        utili = utils.Utils(ui, testing= True, showhelp = False)
        utili.processLoop()
        jjj = 'tjej'
        pass
    
    def testrecallMacroNames(self): pass
    def testrecallAllNames(self): pass
    def testresetCmdNames(self): pass
    def testrecallMacroDeffinitions(self): pass
    
    def teststr(self):
        ui = userinput.UserInput()
        ui.commPort = Testutils.sdevice
        utili = utils.Utils(ui, testing= False, showhelp = False)                
        self.assertEqual('testing:False, cmds: -rmn, -ran, -rmd, -cacn, -q', str(utili))        
        utili = utils.Utils(ui, testing= True, showhelp = False)  
        self.assertEqual('testing:True, cmds: -rmn, -ran, -rmd, -cacn, -q', str(utili))
        pass

if __name__ == '__main__':
    unittest.main()    