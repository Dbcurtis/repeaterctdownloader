#!/usr/bin/env python3
"""
Test file for dlxii
"""
from __future__ import print_function
import os
import sys
import dlxii
import unittest


class TestControllerspecific(unittest.TestCase):

    def setUp(self):
        pass 

    def tearDown(self):
        pass           

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def testcreation(self):
        cs = dlxii.DlxII()
        self.assertEqual('RLC-Club Deluxe II v2.15', cs.get_Ctr_type())
        cpsData = cs.cpsData
        cps0 = cpsData[0]
        self.assertEqual('[CPS: 960, 0.215]', str(cps0))
        self.assertEqual(9600, cps0.bps)
        self.assertTrue(0.21 < cps0.cpsDelay < 0.22)
        ss = '[CPS: 960, 0.215]'
        self.assertEqual(ss, str(cps0))
        rates = [d.bps for d in cs.cpsData]
        self.assertEqual([9600, 19200, 4800, 2400, 1200, 600, 300] , rates)
        css = '[Dlxii: rename:Command number\\s+(\\d\\d\\d)\\s+is\\s+named' \
            '\\s+([0-9a-z]+)\\..*, macrodef:.*contains\\s+[1-9]([0-9]+)?\\s+commands.*]'
        self.assertEqual(css, str(cs))
        pass

    def testfmtN054(self):
        cs = dlxii.DlxII()
        r = cs.fmtN054("junk test")
        self.assertEqual("junk test", r[0])
        self.assertEqual({}, r[1])
        mdf = """DTMF>N054 501N054501
Macro 501 contains 2 commands: 
  #00  Command #038 with 00 digits of data: 
  #01  Command #000 with 02 digits of data: 13
This macro is 9 percent full
OK
OK
DTMF>"""
        r = cs.fmtN054(mdf)
        ii = 2
        pass

if __name__ == '__main__':
    unittest.main()    