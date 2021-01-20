#!/usr/bin/env python3
"""
Test file for getports
"""
from __future__ import print_function
import unittest
#import context
import getports

class TestGetPorts(unittest.TestCase):

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

    def testall(self):
        print(getports.GetPorts().get())


if __name__ == '__main__':
    unittest.main()
