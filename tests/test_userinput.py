#!/usr/bin/env python3
"""
Test file for userinput
"""

from __future__ import print_function
import sys
import unittest
import dlxii
import serial
import myserial
import userinput
import getports

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

class Testuserinput(unittest.TestCase):
    sdevice = ""
    gsp = serial.Serial()

    def setUp(self):
        mySPortclass = myserial.MySerial
        sp = mySPortclass(dlxii.DlxII())
        sp.port = Testuserinput.sdevice
        sp.baudrate = 9600
        sp.timeout = 1.5
        sp.open()
        if sp.isOpen():
            sp.close()
        Testuserinput.gsp = sp
        mySPortclass._debugging = True

    def tearDown(self):
        if Testuserinput.sdevice:
            sp = Testuserinput.gsp
            if sp.isOpen():
                sp.close()
            myserial.MySerial._debugging = False

    @classmethod
    def setUpClass(cls):
        #ports = serial.tools.list_ports.comports()
        devs = getports.GetPorts().get()
        if not devs:
            eprint("No serial ports exist.")
            raise SystemExit("no serial ports exist")
        sp = serial.Serial()
        sp.baudrate = 1200
        sp.timeout = .5

        for dev in devs:
            sp.port = dev
            if not sp.isOpen():
                break

        Testuserinput.sdevice = sp.port
        assert Testuserinput.sdevice
        assert not sp.isOpen()
        sp.open()
        openresult = sp.isOpen()
        if sp.isOpen():
            sp.close()
        myserial.MySerial._debugging = True
        myserial.MySerial._debugreturns = [b'ok\nDTMF>']
        myserial.MySerial._dbidx = 0
        assert openresult

    @classmethod
    def tearDownClass(cls):
        sp = Testuserinput.gsp
        if sp.isOpen():
            sp.close()
        myserial.MySerial._debugging = False
        myserial.MySerial._debugreturns = [b'ok\nDTMF>']
        myserial.MySerial._dbidx = 0

    def testopen(self):
        self.assertTrue(myserial.MySerial._debugging)
        ui = userinput.UserInput()
        ui.inputfn = "cmdreadertest.txt"
        ui.comm_port = Testuserinput.sdevice
        self.assertTrue(ui.open(detect_br=False))
        sp = ui.serial_port
        self.assertTrue(sp.isOpen())
        self.assertEqual(Testuserinput.sdevice, sp.port)
        self.assertEqual(9600, sp.baudrate)
        ui.close()
        ui.close()
        self.assertFalse(sp.isOpen())
        self.assertFalse(ui.serial_port.isOpen())
        # prep for test with baudrate finder
        myserial.MySerial._dbidx = 0
        myserial.MySerial._debugreturns = [
            b'preread ignored', b'9600 fail try 1 MF>',
            b'preread ignored', b'9600 fail try 2 MF>',
            b'preread ignored', b'19200 fail try 1 TMF>',
            b'preread ignored', b'19200 succeed try 2 DTMF>']

        self.assertTrue(ui.open())
        self.assertEqual(19200, sp.baudrate)
        self.assertTrue(sp.isOpen())
        ui.close()


        myserial.MySerial._debugreturns = [
            b'preread ignored', b'9600 fail try 1 MF>',
            b'preread ignored', b'9600 fail try 2 MF>',
            b'preread ignored', b'19200 fail try 1 TMF>',
            b'preread ignored', b'19200 succeed try 2 DTMF>']
        myserial.MySerial._dbidx = 0

        ui.open(detect_br=False)
        self.assertEqual(9600, sp.baudrate)  #9600 is the default
        ui.close()

    def testclose(self): pass  # tested other places

    def testrequest(self):
        fakeuser = ['', 'wrongport']
        try:
            ui = userinput.UserInput(testdata=fakeuser)
            ui.request()
            self.assertTrue(False, msg="did not fault on empty debug list")
        except IndexError:
            pass

        ports = getports.GetPorts().get()
        fakeuser += getports.GetPorts().get() + ['junk', 'dlx2', 'mytest.txt']
        ui = userinput.UserInput(testdata=fakeuser)
        ui.request()
        self.assertEqual(ports[0], ui.comm_port)
        self.assertEqual('mytest.txt', ui.inputfn)
        self.assertTrue(isinstance(ui.controller_type, dlxii.DlxII))

if __name__ == '__main__':
    unittest.main()
