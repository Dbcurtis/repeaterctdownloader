#!/usr/bin/env python3
"""
Test file for MySerial
"""
from __future__ import print_function

import sys
import unittest
import getports
import serial
import myserial
import dlxii

#from serial.tools import list_ports


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


class TestMySerial(unittest.TestCase):
    sdevice = ""
    gsp = serial.Serial()

    def setUp(self):
        myclass = myserial.MySerial
        sp = myclass(dlxii.Device())
        sp.port = TestMySerial.sdevice
        sp.baudrate = 9600
        sp.timeout = 1.5
        sp.open()
        if sp.isOpen():
            sp.close()
        TestMySerial.gsp = sp
        myclass._debugging = True

    def tearDown(self):
        if TestMySerial.sdevice:
            sp = TestMySerial.gsp
            if sp.isOpen():
                sp.close()
            myserial.MySerial._debugging = False

    @classmethod
    def setUpClass(cls):
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

        TestMySerial.sdevice = sp.port
        assert TestMySerial.sdevice
        assert not sp.isOpen()
        sp.open()
        openresult = sp.isOpen()
        if sp.isOpen():
            sp.close()
        assert openresult

    @classmethod
    def tearDownClass(cls):
        sp = TestMySerial.gsp
        if sp.isOpen():
            sp.close()

    def testspOK(self):
        sp = TestMySerial.gsp
        sp.open()
        msclass = myserial.MySerial
        msclass._dbidx = 0
        msclass._debugreturns = [b'preread ignored', b'kjljjglkjerrl',
                                 b'preread ignored', b'9600 succeed DTMF>']
        self.assertFalse(sp.sp_ok())
        self.assertTrue(sp.sp_ok())
        sp.close()

    def testfindBaud(self):
        """
        1) test that an open correct speed port is detected
        2) test that a closed correct speed port is detected
        3) test that a closed first attempt  for 9600 is ok
        4) test that a open second attemtp for 9600 is ok
        5) test that a first attempt at 19200 is ok
        6) test special case of msclass._dbidx = -1 is ok

        """

        sp = myserial.MySerial(dlxii.Device())
        msclass = myserial.MySerial
        TestMySerial.gsp = sp
        msclass._debugging = True

        # test 1) findBaudRate open, 9600
        msclass._dbidx = 0
        msclass._debugreturns = [b'preread ignored',
                                 b'9600 open default succeed DTMF>']

        sp.port = TestMySerial.sdevice
        sp.baudrate = 9600
        sp.timeout = 1.5
        sp.open()
        self.assertTrue(sp.find_baud_rate())
        self.assertEqual(9600, sp.baudrate)
        self.assertTrue(sp.isOpen())

        # test 2) findBaudRate close, 9600
        sp.close()
        msclass._dbidx = 0
        msclass._debugreturns = [b'preread ignored',
                                 b'9600 close default succeed DTMF>']
        self.assertTrue(sp.find_baud_rate())
        self.assertEqual(9600, sp.baudrate)
        self.assertFalse(sp.isOpen())

        # test 3) findBaudRate close bad baud, found 9600 baud
        msclass._dbidx = 0
        msclass._debugreturns = [
            b'preread ignored', b'any fail DMF>',
            b'preread ignored', b'9600 close first scan succeed DTMF>']

        self.assertTrue(sp.find_baud_rate())
        self.assertEqual(9600, sp.baudrate)
        self.assertFalse(sp.isOpen())

        # test 4) findBaudRate open bad baud, found 9600 baud
        msclass._dbidx = 0
        msclass._debugreturns = [
            b'preread ignored', b'kjljjglkjerrl',
            b'preread ignored', b'kjljjglkjerrl',
            b'preread ignored', b'9600 open second scan succeed DTMF>']
        sp.open()
        self.assertTrue(sp.find_baud_rate())
        self.assertEqual(9600, sp.baudrate)
        self.assertTrue(sp.isOpen())

        # test 5) test that a first attempt at 19200 is ok
        msclass._dbidx = 0
        msclass._debugreturns = [
            b'preread ignored', b'9600 fail try 1 MF>',
            b'preread ignored', b'9600 fail try 2 MF>',
            b'preread ignored', b'19200 fail try 1 TMF>',
            b'preread ignored', b'19200 succeed try 2 DTMF>']
        self.assertTrue(sp.find_baud_rate())
        self.assertEqual(19200, sp.baudrate)
        self.assertTrue(sp.isOpen())

        # test 6) check that dbidx = -1 does as expected
        msclass._dbidx = -1
        self.assertEqual(b'OK\nDTMF>', sp.dread(99)[0])

        msclass._dbidx = 0
        sp.close()


if __name__ == '__main__':
    unittest.main()
