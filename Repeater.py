#!/usr/bin/env python3

import os
import sys
import myserial
import serial
import re
import userinput
import dlxii
import commandreader
import controller
import getports
#import argparse
from pathlib import Path



_debugging = False

#_parser = argparse.ArgumentParser()
#_parser.add_argument('-q','--quit', help = 'quit the', action = "store_true")
#_parser.add_argument('-ran','--recall_all_names', help = 'return all renamed commands', action = "store_true")
#_parser.add_argument('-rmd','--recall_macro_def', help = 'return all macro deffinitions', action = "store_true")
#_parser.add_argument('-cacn','--reset_all_comd_names', help = 'reset all command names', action = "store_true")
#_parser.add_argument('-q','--quit', help = 'quit the util', action = "store_true")

#
# doit() reads the commands from the file and sends them to the controller
def sendSpecifiedFile():
    global ui
    ui.open()
    sp = ui.serial_port
    c = controller.Controller(ui)
    cr = commandreader.CommandReader(ui)
    cr.open()
    c.open()    
    try:       
        while True:
            line = cr.get()
            if line=="":break
            c.sendcmd(line,  echoit = _debugging)    
        cr.close()
        c.close()
    finally:
        if sp.isOpen():sp.close()
        c.close()
        cr.close()

def sendFile():
    global ui
    ui.inputfn = input("file name to send to repeater?>")
    sendSpecifiedFile()

def _cmdloop(c):
    print("Quit or Exit to exit command mode")
    while True:        
        cmd = input("input>")
        cmd = cmd.strip().upper()
        if cmd.startswith('Q') or cmd.startswith('E'):
            print("Exiting command input mode...")
            break
        c.sendcmd(cmd, echoit = _debugging)

def sendUsersCmds():
    global ui
    ui.open()
    c = controller.Controller(ui)
    c.open()
    try:
        _cmdloop(c)
        c.close()        
    finally:
        if ui.serial_port.isOpen():ui.serial_port.close()
        c.close()
       # cr.close()  
    


                
def doUtilityCmds():
    global ui
    ui.inputfn = request("input log file name.txt")
    ui.open()
    c = controller.Controller(ui)
    c.open()
    try:
        utils = Utility(ui)
        utils.processLoop()
        c.close()        
    finally:
        if ui.serial_port.isOpen():ui.serial_port.close()
        c.close()
        cr.close()  
    
    
    
    pass

def _getports():
    
    allports = getports.GetPorts().get()
    if not allports:
        eprint("No serial ports exist.")
        raise SystemExit("no serial ports exist")         
    sp = serial.Serial()
    sp.baudrate=9600
    sp.timeout=.5

    availablePorts = [ ]
    for p in allports:
        sp.port=p
        if not sp.isOpen():availablePorts.append(p)
    return availablePorts

def shutdown():
    pass

def main():
    global ui

    availablePorts = _getports()
    print("Available serial ports are: %s" % availablePorts)

    ui = userinput.UserInput()
    ui.request()
    sendSpecifiedFile()
    while True:  
        response = input("Type 'Q' to quit\n"
                         "Type 'M' for manual commands\n"
                         "type 'U' for Utility operations\n"
                         "Type 'F' for file transfer (Q/F/M/U)?>").lower()
        if response.startswith('q'):break
        if response.startswith('f'):sendFile()
        if response.startswith('m'):sendUsersCmds()
        if response.startswith('U'):doUtilityCmds()
        else:print("only type one of Q, M, U, or F")

    shutdown()   

if __name__ == '__main__':
    main()


            