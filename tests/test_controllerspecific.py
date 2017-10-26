#!/usr/bin/env python3
"""
Test file for controllerspecific
"""
from __future__ import print_function
import os
import sys
import controllerspecific
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
        cs = controllerspecific.ControllerSpecific()
        self.assertEqual('Abstract Controller', cs.get_Ctr_type())
        cpsData = cs.cpsData
        cps0 = cpsData[0]
        self.assertEqual('[CPS: 960, 0.215]', str(cps0))
        self.assertEqual(9600, cps0.bps)
        self.assertTrue(0.21 < cps0.cpsDelay < 0.22)
        ss = '[CPS: 960, 0.215]'
        self.assertEqual(ss, str(cps0))
        rates = [d.bps for d in cs.cpsData]
        self.assertEqual([9600, 19200, 4800, 2400, 1200, 600, 300] , rates)
        css = '[ControllerSpecific: rename:.*, macrodef:.*]'
        self.assertEqual(css, str(cs))
        pass

    def testfmtN054(self):
        cs = controllerspecific.ControllerSpecific()
        r = cs.fmtRMC("junk test")
        self.assertEqual("junk test", r[0])
        self.assertEqual({}, r[1])  
        pass
    
if __name__ == '__main__':
    unittest.main()    