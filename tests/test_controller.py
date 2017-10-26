#!/usr/bin/env python3
"""
Test file for controller
"""
from __future__ import print_function
import os
import sys
import dlxii
import unittest
import userinput
import controller
import serial
import myserial
import time
import getports


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

class TestController(unittest.TestCase):
    ui = userinput.UserInput()
    ui1 = userinput.UserInput()
    sdevice = ""
    
        
    def setUp(self):
        mySPortclass =  myserial.MySerial
        mySPortclass._debugging = True
        mySPortclass._debugreturns =  [b'ok\nDTMF>']
        mySPortclass._dbidx=0 

    def tearDown(self):
        mySPortclass =  myserial.MySerial
        mySPortclass._debugging = False
        mySPortclass._debugreturns =  [b'ok\nDTMF>']
        mySPortclass._dbidx=0         

    @classmethod
    def setUpClass(cls):
        mySPortclass =  myserial.MySerial
        devs = getports.GetPorts().get()
        if not devs:
            eprint("No serial ports exist.")
            raise SystemExit("no serial ports exist")
        sp = serial.Serial()
        sp.baudrate=9600
        sp.timeout=.5
        
        for dev in devs:
            sp.port=dev
            if not sp.isOpen():
                break
        
        TestController.sdevice=sp.port
        assert (len(TestController.sdevice)>0)           
        assert(not sp.isOpen())
        sp.open()    
        openresult= sp.isOpen()
        if sp.isOpen():sp.close() 
        assert(openresult)
        ui =  TestController.ui
        ui.comm_port = sp.port
        ui.inputfn = 'testcontroller.txt'
        
        ui1 =  TestController.ui1
        ui1.comm_port = sp.port
        ui1.inputfn = ''
        
        mySPortclass._debugging = True
        mySPortclass._debugreturns =  [b'ok\nDTMF>']
        mySPortclass._dbidx=0 
        ui.open(detect_br=False)
        ui.close()
        
        mySPortclass._dbidx=0
        ui1.open(detect_br=False)
        ui1.close()

    @classmethod
    def tearDownClass(cls):
        mySPortclass =  myserial.MySerial
        sp = TestController.ui.serial_port
        if sp.isOpen():sp.close()
        mySPortclass._debugging= False
 
    
    def testopen(self):
        mySPortclass =  myserial.MySerial
        c = controller.Controller(TestController.ui)
        mySPortclass._debugreturns =  [b'ok\nDTMF>', b'ok\nDTMF>']
        mySPortclass._dbidx=0        
        self.assertTrue(c.open())
        self.assertTrue(c.isOpen)
        self.assertTrue(c.isFilesOpen)
        self.assertTrue(c.sp.isOpen())
        self.assertEquals('testcontroller.cmdlog.txt', c.cLFile.name)
        self.assertEquals('testcontroller.exelog.txt', c.cEFile.name)
        c.close()
       
        c = controller.Controller(TestController.ui1)        
        mySPortclass._debugreturns =  [b'ok\nDTMF>', b'ok\nDTMF>']
        mySPortclass._dbidx=0
        self.assertTrue(c.open())
        self.assertTrue(c.isOpen)
        self.assertTrue(c.isFilesOpen)        
        self.assertTrue(c.sp.isOpen())
        self.assertEquals('test.cmdlog.txt', c.cLFile.name)        
        self.assertEquals('test.exelog.txt', c.cEFile.name)
        c.close()

    
    def testclose(self):
        mySPortclass =  myserial.MySerial
        c = controller.Controller(TestController.ui)
        mySPortclass._debugreturns =  [b'ok\nDTMF>', b'ok\nDTMF>']
        mySPortclass._dbidx=0        
        self.assertTrue(c.open())
        self.assertTrue(c.isOpen)
        self.assertTrue(c.isFilesOpen)        
        c.close()
        self.assertFalse(c.isOpen)
        self.assertFalse(c.isFilesOpen)
        self.assertFalse(c.sp.isOpen())
    
    def testsendcmd(self):
        mySPortclass =  myserial.MySerial
        c = controller.Controller(TestController.ui1)
        mySPortclass._debugreturns =  [ b'ok\nDTMF>' for i in range(40)]
        mySPortclass._dbidx=0
        self.assertTrue(c.open())
        c.sendcmd("")
        self.assertFalse(c.lastCmd)
        c.sendcmd("; this is a comment that ends up blank \n")
        self.assertFalse(c.lastCmd)
        c.sendcmd("009")
        self.assertEqual("009\r", c.lastCmd)
        c.sendcmd("009;this is a comment")
        self.assertEqual("009\r", c.lastCmd)
        c.sendcmd("010 ;this is a comment")
        self.assertEqual("010\r", c.lastCmd)        
        c.sendcmd("  0  0 9  ")
        self.assertEqual("009\r", c.lastCmd)
        
        mySPortclass._debugreturns =  [
            b'Error: test\n'
            b'ok\nDTMF>']
        
        mySPortclass._dbidx=0
        self.assertFalse(c.sendcmd("  0  0 9  "))
        self.assertTrue(c.lastResponse.find("E R R O R") > 0)
        c.close()
        fct = os.path.getmtime('test.exelog.txt')
        ofct = fct
        self.assertTrue( 1.0 > abs(fct - c.openTime))
        
        ff = open('test.exelog.txt', 'r', encoding='utf-8')
        lines = ff.readlines(999)
        
        self.assertTrue(lines[1].startswith(';---'))
        self.assertTrue(lines[3].startswith(';---'))
        fid = lines[2].split(', ')
        self.assertTrue(fid[0].startswith('; File:'))
        self.assertTrue(fid[1].startswith('Created on:'))
        self.assertTrue(fid[2].endswith('UTC\n'))
        lastOpened = c.whenOpened
        lol = lastOpened.split(', ')
        self.assertTrue(fid[1].endswith(lol[0]))
        self.assertTrue(fid[2].startswith(lol[1]))
        content = ''.join(lines)
        self.assertEquals(2, len(content.split('Error:')))
        self.assertEquals(2, len(content.split('*E R R O R*')))
        
        ff = open('test.cmdlog.txt', 'r', encoding='utf-8')
        lines = ff.readlines(999)
        ff.close()
        
        print("need to handle cmdlog.txt")
                        
        time.sleep(3)
        #  
        lui = userinput.UserInput()
        lui.comm_port = TestController.ui.comm_port
        lui.open(detect_br=False)
        c = controller.Controller(lui)
        mySPortclass._debugreturns =  [ b'ok\nDTMF>' for i in range(40)]
        mySPortclass._dbidx=0      
        self.assertTrue(c.open())
        c.sendcmd('009')
        response = c.lastResponse
        c.close()
        fct = os.path.getmtime('test.exelog.txt')
        self.assertTrue( 1.0 > abs(fct - c.openTime))
        self.assertTrue(1.0 < abs(fct - ofct))    
        nf = open(c.cEfn, 'r', encoding='utf-8')
        lines = nf.readlines(99999)
        nf.close()
        #  by here pretty sure the standard operations are working ok
        #  now need to try some of the filters
        mySPortclass._debugreturns =  [
            b'ok no filter -- DTMF>',
            b'ok no display but log -- DTMF>',
            b'ok no log but display -- DTMF>',
            b'ok no log no display -- DTMF>',
            b'ok no display but log selected -- DTMF>',
            b'ok display but log deselected -- DTMF>',
            b'ok format -- DTMF>',
        ]
        mySPortclass._dbidx=0        
        
        c = controller.Controller(lui)
        c.open()
        mySPortclass._dbidx=0 
        c.sendcmd('009 ;no filter')
        c.sendcmd('010 ;no display but log', display= False)
        c.sendcmd('011 ;no log but display', logIt = False)
        c.sendcmd('012 ;no log no display', logIt = False, display= False)
        c.sendcmd('013 ;no display but log selected', display= False, selectIt=lambda a:True)
        c.sendcmd('014 ;display but log deselected', display= True, selectIt=lambda a:False)
        c.sendcmd('015 ;display log, format', formatIt= lambda a: 'fmt ' + a)
        c.close()
        ff = open('test.exelog.txt', 'r', encoding='utf-8')
        lines = ff.readlines(999)
        ff.close()
        self.assertEquals(10, len(lines))
   
        
    def testB2S(self):
        b2s = controller.Controller.Byte_2_String
        tests =  'this is a test\n'
        s = b2s(b'this is a test\n')
        self.assertEqual(tests, s)

    
    def testS2B(self):
        s2b =  controller.Controller.String_2_Byte
        input =  'this is a test\n'
        testb = b'this is a test\n'
        b = s2b(input)
        self.assertEqual(testb, b)
     

    
    if __name__ == '__main__':
        unittest.main()    