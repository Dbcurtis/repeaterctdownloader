#!/usr/bin/env python3
"""
Test file for controllerspecific
"""
from __future__ import print_function
import os
import sys
import controllerspecific
import unittest



def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

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
        cs = controllerspecific(9600, .25)
        self.assertEqual(9600, cs.bps)
        self.assertEqual(0.25, cs.cpsDelay)
        ss = str(cs)
        self.assertEquals(ss, str(cs))
        rates = [d.bps for d in cs.cpsData]
        self.assertEqual([9600, 19200, 4800, 2300, 1200, 600, 300] , rates)
        cpsd = cs.cpsData
        l0 = cpsd[0]
        sss = str(l0)
        self.assertEquals("", str(l0))     
        pass

    def testfmt054(self):
        cs = controllerspecific(9600, .25)
        r = cs.fmt054("junk test")
        self.assertEqual("junk test", r[0])
        self.assertEqual({}, r[1])  
        pass
    

    
    def teststr(self):

        pass

if __name__ == '__main__':
    unittest.main()    