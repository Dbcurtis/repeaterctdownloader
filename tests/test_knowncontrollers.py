#!/usr/bin/env python3
"""
Test file for knowncontrollers
"""
from __future__ import print_function
import unittest
import knowncontrollers
import dlxii

class TestKnownControllers(unittest.TestCase):

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

    def test_creation(self):
        classknown = knowncontrollers.KnownControllers.get_known()
        kc = knowncontrollers.KnownControllers()
        objknown = str(kc)
        self.assertEqual(classknown, objknown)


    def test_getcontrollerids(self):
        aa = knowncontrollers.KnownControllers.get_controller_ids()
        exp = ["RLC-Club Deluxe II v2.15", "RLC1 Plus"]
        self.assertEqual(exp, aa)

    def test_select_controller(self):
        self.assertEqual(None, knowncontrollers.KnownControllers.select_controller(''))
        self.assertEqual(None, knowncontrollers.KnownControllers.select_controller('junk'))
        self.assertTrue(isinstance(knowncontrollers.KnownControllers.select_controller('dlx2'), dlxii.DlxII))


if __name__ == '__main__':
    unittest.main()
