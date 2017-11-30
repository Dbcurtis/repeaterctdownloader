#!/usr/bin/env python3
""" TO BE DONE """
import serial
import serial.tools.list_ports

class GetPorts:
    """GetPorts Class determines what communication ports exist on the executing computer

    The version of serial is used to determine how list port works.

    Usage:
    devs = getports.GetPorts().get()

    every call to get() refreshes the port tuple.
    Thus, you can take out and insert ports at any time.
    """

    oldSerial = False
    try:
        j = serial.__version__
    except AttributeError:
        oldSerial = True

    def __init__(self):
        self.devs = []


    def get(self):
        """get()

        TBD
        """
        ports = serial.tools.list_ports.comports()
        devs = []

        if GetPorts.oldSerial:
            devs = [p for p in [port[0] for port in ports]]
        else:
            devs = [port.device for port in ports]

        self.devs = [p for p in devs]
        return self.devs

    def get_last(self):
        """get_last()
        TBD
        """
        return self.devs

if __name__ == '__main__':
    PORTS = GetPorts().get()
    if PORTS:
        print(PORTS)
    else:
        print("No ports found or all found ports busy")
