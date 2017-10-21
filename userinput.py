#!/usr/bin/env python3
import os
import sys
import myserial
import getports
import dlxii

class UserInput:
    """UserInput()

    obtains user input for which serial port to use and a path for
    an input file to be read.  
    """
    
    def __init__(self):
        self.commPort = ""
        self.inputfn = ""
        controller_type =  dlxii.DlxII()
        self.serial_port =myserial.MySerial(controller_type)

    def __str__(self):
        return '[UserInput: %s]' % (self.commPort + ", " + self.inputfn)

    def __repr__(self):
        return '[UserInput: %s]' % (self.commPort + ", " + self.inputfn)

    def request(self):
        """request()

        Request comm port id and filename containing controller commands
        """
        self.commPort = input("Comm Port for repeater? ")
        self.inputfn = input("file name to send to repeater or blank")

    def close(self):
        """close()

        Closes the serial port if it is open
        """
        if self.serial_port.isOpen():
            self.serial_port.close()

    def open(self, detectBR = True):
        """open()

        Configures and opens the serial port if able, otherwise
         displays error with reason.
         (if the serial port is already open, closes it and re opens it)

        If the serial port is opened and if detectBR: the baud rate of the controller is
        found and the serial port so set.

        If detectBR is True, the baud rate will be detected by establishing
        communication with the controller
        
        If the serial port is opened, returns True, False otherwise
        
        thows exception if no baud rate is found
        """
        sp=self.serial_port
        try:         
            sp.port = self.commPort  # '/dev/ttyACM0'          
            sp.timeout = .2
            sp.baudrate = 9600
            if sp.isOpen():
                sp.close()
            sp.open()
            
        except myserial.serialutil.SerialException as e:
            self.commPort = ""
            print(e)
            return False

        if detectBR:
            if not sp.findBaudRate():
                raise OSError('Unable match controller baud rate')
        return True

if __name__ == '__main__':
    print(getports.GetPorts().get())
    ui = UserInput()
    ui.request()
    ui.open()
    print("success on open")
    ui.close()
    