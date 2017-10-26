#!/usr/bin/env python3

import os
import sys
import myserial
import serial
import re
import userinput
import getports
import dlxii
import commandreader
import controller
import getports
from pathlib import Path


_debugging = False


def _sendSpecifiedFile(ui):
    """_sendSpecifiedFile()
    
    ui is a UserInput
    
    opens the controller, the commandreader, and
    sends each line to the controller.
    
    """
    ui.open()
    sp = ui.serial_port
    c = controller.Controller(ui)
    cr = commandreader.CommandReader(ui)
    cr.open()
    c.open()    
    try:       
        while True:
            line = cr.get()
            if line=="":break  #exit when file read
            c.sendcmd(line,  echoit = _debugging)    
        cr.close()
        c.close()
    finally:
        c.close()
        cr.close()
        ui.close()

def sendFile(ui):
    """sendFile()
    
    asks for a file name and invokes _sendSpecifiedFile
    """
 
    ui.inputfn = input("file name to send to repeater?>")
    _sendSpecifiedFile(ui)
    

def _cmdloop(c):
    """_cmdloop(c)
    
    c is a controller.
    prints the exit command info,
    Accepts a command from the user, sends it to the controller and displays the result.
    
    Loop exits on a command starting with a q or e
    
    """
    print("Quit or Exit to exit command mode")
    while True:        
        cmd = input("input>")
        cmd = cmd.strip().upper()
        if cmd.startswith('Q') or cmd.startswith('E'):
            print("Exiting command input mode...")
            break
        c.sendcmd(cmd, echoit = _debugging)

def sendUsersCmds(ui):
    """sendUsersCmds()
    
    Opens the ui and controller,
    runs the command loop
    closes the controller and the ui.
    
    """
    
    ui.open()
    c = controller.Controller(ui)
    c.open()
    try:
        _cmdloop(c)
             
    finally:
        c.close()
        ui.close()
    

               
def doUtilityCmds(ui):
    """doUtilityCmds()
    
    Asks for the log file name, opens the ui, and the controller.
    Calls the util processor loop,
    Closes the controller and the ui on exit
    """
    
    ui.inputfn = request("input log file name.txt")
    ui.open()
    c = controller.Controller(ui)
    c.open()
    try:
        utils = Utility(ui)
        utils.processLoop()       
    finally:
        c.close()
        ui.close()

def main():
    """main()
    
    Identifies the avilable ports, gets user input, sends the specified file (if exists) to
    the controller.
    
    Prints the command list and processes the user selected command(s)
    
    """
    global ui

    availablePorts = getports.GetPorts.get()
    print("Available serial ports are: %s" % availablePorts)

    ui = userinput.UserInput()
    ui.request()
    try:       
        ui.open()
        _sendSpecifiedFile(ui)
        while True:  
            response = input("Type 'Q' to quit\n"
                             "Type 'M' for manual commands\n"
                             "type 'U' for Utility operations\n"
                             "Type 'F' for file transfer (Q/F/M/U)?>").lower()
            if response.startswith('q'):break
            if response.startswith('f'):sendFile(ui)
            if response.startswith('m'):sendUsersCmds(ui)
            if response.startswith('U'):doUtilityCmds(ui)
            else:print("only type one of Q, M, U, or F")
    finally:
        ui.close()   

if __name__ == '__main__':
    try:
        main()
    except(Exception, KeyboardInterrupt) as exc:
        sys.exit(str(exc))


            