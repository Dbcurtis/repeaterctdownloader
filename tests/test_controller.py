#!/usr/bin/env python3
"""
Test file for controller
"""
from __future__ import print_function
import os
import sys
import time
import sys
import os
import unittest
#import context
ppath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ppath)
#import context
import userinput
import controller
import serial
import myserial
import getports
import dlxii


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


class TestController(unittest.TestCase):
    ui = userinput.UserInput(dlxii.Device())
    ui1 = userinput.UserInput(dlxii.Device())
    sdevice = ""

    def setUp(self):
        mySPortclass = myserial.MySerial
        mySPortclass._debugging = True
        mySPortclass._debugreturns = [b'ok\nDTMF>']
        mySPortclass._dbidx = 0

    def tearDown(self):
        mySPortclass = myserial.MySerial
        mySPortclass._debugging = False
        mySPortclass._debugreturns = [b'ok\nDTMF>']
        mySPortclass._dbidx = 0

    @classmethod
    def setUpClass(cls):
        mySPortclass = myserial.MySerial
        devs = getports.GetPorts().get()
        if not devs:
            eprint("No serial ports exist.")
            raise SystemExit("no serial ports exist")
        sp = serial.Serial()
        sp.baudrate = 9600
        sp.timeout = .5

        for dev in devs:
            sp.port = dev
            if not sp.isOpen():
                break

        TestController.sdevice = sp.port
        assert TestController.sdevice
        assert not sp.isOpen()
        sp.open()
        openresult = sp.isOpen()
        if sp.isOpen():
            sp.close()
        assert openresult
        ui = TestController.ui
        ui.comm_port = sp.port
        ui.inputfn = 'testcontroller.txt'

        ui1 = TestController.ui1
        ui1.comm_port = sp.port
        ui1.inputfn = ''

        mySPortclass._debugging = True
        mySPortclass._debugreturns = [b'ok\nDTMF>']
        mySPortclass._dbidx = 0
        ui.open(detect_br=False)
        ui.close()

        mySPortclass._dbidx = 0
        ui1.open(detect_br=False)
        ui1.close()

    @classmethod
    def tearDownClass(cls):
        mySPortclass = myserial.MySerial
        sp = TestController.ui.serial_port
        if sp.isOpen():
            sp.close()
        mySPortclass._debugging = False

    def test_0inst(self):
        from sys import platform as _platform
        mySPortclass = myserial.MySerial
        c = controller.Controller(TestController.ui)
        #sss = str(c)
        #platform.system()
        sexp = '[Controller: False, False, [UserInput: COM4, testcontroller.txt]]'
        rexp = '[Controller: False, False, False, [UserInput: COM4, testcontroller.txt]]'
        self.assertEquals(sexp, str(c))
        self.assertEquals(rexp, repr(c))

    def testopen(self):
        mySPortclass = myserial.MySerial
        c = controller.Controller(TestController.ui)
        mySPortclass._debugreturns = [b'ok\nDTMF>', b'ok\nDTMF>']
        mySPortclass._dbidx = 0
        self.assertTrue(c.open())
        # self.assertTrue(c.isOpen)
        self.assertTrue(c.atts['isOpen'])
        self.assertTrue(c.atts['is_files_open'])
        self.assertTrue(c.s_port.isOpen())
        self.assertEqual('testcontroller.cmdlog.txt',
                         c.atts['cmd_log_file'].name)
        self.assertEqual('testcontroller.exelog.txt',
                         c.atts['cmd_err_file'].name)
        c.close()

        c = controller.Controller(TestController.ui1)
        mySPortclass._debugreturns = [b'ok\nDTMF>', b'ok\nDTMF>']
        mySPortclass._dbidx = 0
        self.assertTrue(c.open())
        # self.assertTrue(c.isOpen)
        self.assertTrue(c.atts['isOpen'])
        self.assertTrue(c.atts['is_files_open'])
        self.assertTrue(c.s_port.isOpen())
        self.assertEqual('test.cmdlog.txt', c.atts['cmd_log_file'].name)
        self.assertEqual('test.exelog.txt', c.atts['cmd_err_file'].name)
        c.close()

    def testclose(self):
        mySPortclass = myserial.MySerial
        c = controller.Controller(TestController.ui)
        mySPortclass._debugreturns = [b'ok\nDTMF>', b'ok\nDTMF>']
        mySPortclass._dbidx = 0
        self.assertTrue(c.open())
        # self.assertTrue(c.isOpen)
        self.assertTrue(c.atts['isOpen'])
        self.assertTrue(c.atts['is_files_open'])
        c.close()
        # self.assertFalse(c.isOpen)
        self.assertFalse(c.atts['isOpen'])
        self.assertFalse(c.atts['is_files_open'])
        self.assertFalse(c.s_port.isOpen())

    def testcvntcmd(self):
        mySPortclass = myserial.MySerial
        c = controller.Controller(TestController.ui)
        atext = 'this is ascii'
        bbytes = b'this is bytes'
        btext = 'this is bytes'
        jjj = c._cnvtcmd(atext)
        self.assertEqual(atext, jjj)
        self.assertTrue(isinstance(jjj, str))

        jjj = c._cnvtcmd(bbytes)
        self.assertEqual(btext, jjj)
        self.assertTrue(isinstance(jjj, str))

    def testsendcmd(self):
        mySPortclass = myserial.MySerial
        c = controller.Controller(TestController.ui1)
        mySPortclass._debugreturns = [b'ok\nDTMF>' for i in range(40)]
        mySPortclass._dbidx = 0
        self.assertTrue(c.open())
        c.sendcmd("")
        self.assertFalse(c.atts['last_cmd'])
        c.sendcmd("; this is a comment that ends up blank \n")
        self.assertFalse(c.atts['last_cmd'])
        c.sendcmd("009")
        self.assertEqual("009\r", c.atts['last_cmd'])
        c.sendcmd("009;this is a comment")
        self.assertEqual("009\r", c.atts['last_cmd'])
        c.sendcmd("010 ;this is a comment")
        self.assertEqual("010\r", c.atts['last_cmd'])
        c.sendcmd("  0  0 9  ")
        self.assertEqual("009\r", c.atts['last_cmd'])

        mySPortclass._debugreturns = [
            b'Error: test\n'
            b'ok\nDTMF>']

        mySPortclass._dbidx = 0
        self.assertFalse(c.sendcmd("  0  0 9  "))
        self.assertTrue(c.atts['last_response'].find("E R R O R") > 0)
        c.close()
        fct = os.path.getmtime('test.exelog.txt')
        ofct = fct
        self.assertTrue(abs((fct) - (c.atts['open_time'])) < 1.0)

        _file = open('test.exelog.txt', 'r', encoding='utf-8')
        lines = _file.readlines(999)

        self.assertTrue(lines[1].startswith(';---'))
        self.assertTrue(lines[3].startswith(';---'))
        fid = lines[2].split(', ')
        self.assertTrue(fid[0].startswith('; File:'))
        self.assertTrue(fid[1].startswith('Created on:'))
        self.assertTrue(fid[2].endswith('UTC\n'))
        lastOpened = c.atts['when_opened']
        lol = lastOpened.split(', ')
        self.assertTrue(fid[1].endswith(lol[0]))
        self.assertTrue(fid[2].startswith(lol[1]))
        content = ''.join(lines)
        self.assertEqual(2, len(content.split('Error:')))
        self.assertEqual(2, len(content.split('*E R R O R*')))

        _file = open('test.cmdlog.txt', 'r', encoding='utf-8')
        lines = _file.readlines(999)
        _file.close()

        print("need to handle cmdlog.txt")

        time.sleep(3)
        #
        lui = userinput.UserInput(dlxii.Device())
        lui.comm_port = TestController.ui.comm_port
        lui.open(detect_br=False)
        c = controller.Controller(lui)
        mySPortclass._debugreturns = [b'ok\nDTMF>' for i in range(40)]
        mySPortclass._dbidx = 0
        self.assertTrue(c.open())
        c.sendcmd('009')
        #response = c.last_response
        c.close()
        fct = os.path.getmtime('test.exelog.txt')
        self.assertTrue(abs((fct) - (c.atts['open_time'])) < 1.0)
        self.assertTrue(abs((fct) - (ofct)) < 4.0)
        nf = open(c.atts['cmd_errfile_name'], 'r', encoding='utf-8')
        lines = nf.readlines(99999)
        nf.close()
        #  by here pretty sure the standard operations are working ok
        #  now need to try some of the filters
        mySPortclass._debugreturns = [
            b'ok no filter -- DTMF>',
            b'ok no display but log -- DTMF>',
            b'ok no log but display -- DTMF>',
            b'ok no log no display -- DTMF>',
            b'ok no display but log selected -- DTMF>',
            b'ok display but log deselected -- DTMF>',
            b'ok format -- DTMF>',
        ]
        mySPortclass._dbidx = 0

        c = controller.Controller(lui)
        c.open()
        mySPortclass._dbidx = 0
        c.sendcmd('009 ;no filter')
        c.sendcmd('010 ;no display but log', display=False)
        c.sendcmd('011 ;no log but display', log_it=False)
        c.sendcmd('012 ;no log no display', log_it=False, display=False)
        c.sendcmd('013 ;no display but log selected',
                  display=False, select_it=lambda a: True)
        c.sendcmd('014 ;display but log deselected',
                  display=True, select_it=lambda a: False)
        c.sendcmd('015 ;display log, format', format_it=lambda a: 'fmt ' + a)
        c.close()
        lines = []
        with open('test.exelog.txt', 'r', encoding='utf-8') as _:
            lines = _.readlines(999)
        self.assertEqual(10, len(lines))

    def testB2S(self):
        b2s = controller.BYTE_2_STRING
        tests = 'this is a test\n'
        _ = b2s(b'this is a test\n')
        self.assertEqual(tests, _)

    def testS2B(self):
        s2b = controller.STRING_2_BYTE
        _ = 'this is a test\n'
        testb = b'this is a test\n'
        _ = s2b(_)
        self.assertEqual(testb, _)

    if __name__ == '__main__':
        unittest.main()
