#!/usr/bin/env python3
"""
Test file for controllerspecific
"""
from __future__ import print_function
import unittest
import controllerspecific


class TestControllerspecific(unittest.TestCase):
    """ TBD """
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
        _cs = controllerspecific.ControllerSpecific()
        self.assertEqual('Abstract Controller', _cs.get_Ctr_type())
        _ = _cs.cps_data
        cps0 = _[0]
        self.assertEqual('[CPS: 960, 0.215]', str(cps0))
        self.assertEqual(9600, cps0.bps)
        self.assertTrue(0.21 < cps0.cpsDelay < 0.22)
        #ss = '[CPS: 960, 0.215]'
        self.assertEqual('[CPS: 960, 0.215]', str(cps0))
        rates = [d.bps for d in _cs.cps_data]
        self.assertEqual([9600, 19200, 4800, 2400, 1200, 600, 300], rates)
        css = '[ControllerSpecific: rename:.*, macrodef:.*]'
        self.assertEqual(css, str(_cs))


    def testfmtRMC(self):
        _cs = controllerspecific.ControllerSpecific()
        _r = _cs.fmtRMC("junk test")
        self.assertEqual("junk test", _r[0])
        self.assertEqual({}, _r[1])


if __name__ == '__main__':
    unittest.main()
