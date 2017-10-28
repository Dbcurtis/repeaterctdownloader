#!/usr/bin/env python3
"""
Test file for commandreader
"""
from __future__ import print_function
import os
import sys
from itertools import count
import dlxii
import unittest
import commandreader
import userinput

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

class TestCommandreader(unittest.TestCase):
    ui = userinput.UserInput()
    
    def setUp(self):
        pass

    def tearDown(self):
        pass         

    @classmethod
    def setUpClass(cls):
        TestCommandreader.ui.inputfn="tests/cmdreadertest.txt"



    @classmethod
    def tearDownClass(cls):    
        pass
    
    def testopen(self):
        cr=commandreader.CommandReader(TestCommandreader.ui)
        fcr = None
        try:              
           
            aa = cr.get()
            self.assertTrue(cr.is_closed)
            self.assertEqual("",aa)
            cr.close()
            self.assertTrue(cr.open())
            self.assertFalse(cr.is_closed)
            try:
                cr.open()
                self.assertTrue(False,"did not detect multiple attempts to open")
            except AssertionError:
                pass
            
            cr.close()
            self.assertTrue(cr.is_closed)        
            fakeui = userinput.UserInput()
            fakeui.inputfn='totaljunk.txt'
            fcr = commandreader.CommandReader(fakeui)
            self.assertFalse(fcr.open())
            self.assertEqual("[Errno 2] No such file or directory: 'totaljunk.txt'",str( fcr.lasterror))
            self.assertTrue(fcr.is_closed)
        finally:           
            fcr.close()
            cr.close()
        
    
    def testclose(self):
        pass
    
    def testget(self):
        cr=commandreader.CommandReader(TestCommandreader.ui)
        try:
            
            cr.open()
            lines = []
            
            while True:
                line = cr.get()
                if line=="":break
                lines.append(line)
               
            cr.close()
            self.assertEqual(7,len(lines))
            lastline = lines[6]
            self.assertFalse(lastline.endswith("\n"))
            
            emptyline = lines[5]
            self.assertEqual("\n",emptyline)
            self.assertEqual("line 4\n",lines[3])
        
        finally:
            cr.close()

if __name__ == '__main__':
    unittest.main()
