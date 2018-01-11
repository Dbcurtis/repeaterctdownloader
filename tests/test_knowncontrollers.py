#!/usr/bin/env python3
"""
Test file for knowncontrollers
"""
from __future__ import print_function
import dlxii
import unittest
import knowncontrollers


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
        classknown = knowncontrollers.get_known()
        kc = knowncontrollers.KnownControllers()
        objknown = str(kc)
        self.assertEqual(classknown, objknown)


    def test_getcontrollerids(self):
        aa = knowncontrollers.get_controller_ids()
        exp = ["dlxii", "rlc1plus"]
        self.assertEqual(exp, aa)

    def test_select_controller(self):
        self.assertFalse(knowncontrollers.select_controller(''))
        self.assertFalse(knowncontrollers.select_controller('junk'))
        ctrltup = knowncontrollers.select_controller('dlx2')
        self.assertEqual('dlxii', ctrltup[0])
        self.assertTrue(isinstance(ctrltup[1],  dlxii.Device))
        



if __name__ == '__main__':
    unittest.main()
