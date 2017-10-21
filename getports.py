#!/usr/bin/env python3

import os
import sys
import serial
from serial.tools import list_ports

class GetPorts:
    """GetPorts Class determines what communication ports exist on the executing computer
    
    The version of serial is used to determine how list port works.

    Usage:
    devs = getports.GetPorts().get()
    
    every call to get() refreshes the port list. Thus, you can take out and insert ports at any time.
    """

    oldSerial = False
    try:
        j = serial.__version__
    except:
        oldSerial = True
        
    def __init__(self):
        self.devs = []
        
        
    def get(self):
        ports = serial.tools.list_ports.comports()
        devs = []        
        if GetPorts.oldSerial:
            devs = [port[0] for port in ports]
            for p in ports:
                devs.append(p[0])            
            
        else:
            devs =[port.device for port in ports]
            
        self.devs = devs
        return self.devs
    
    def getLast():
        return self.devs
    
if __name__ == '__main__':
    print(GetPorts().get())
    