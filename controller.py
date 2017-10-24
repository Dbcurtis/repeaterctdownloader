#!/usr/bin/env python3

import os
import sys
import serial
import myserial
import re
import userinput
import getports
from datetime import datetime
from os import path
from time import time


from pathlib import Path

class Controller:
    """Controller Class supports communication of commands to the controller

    c = Controller(ui)
    insantiates a controller using a UserInput object(ui)

    sets up the logging files.  if infil=foo.txt, the command
    log file will be named
    foo.cmdlog.txt and the execution log will be named
    foo.exelog.txt

    The command log is simply the commands that were sent to the controller
    The execution log is a copy of the commands sent and the responses.

    Once the Contoller is instantiated, it needs to be opened before
     use. Closed after use.

    The controller replys are sent to stdout as well as to the logging files


    c=Controller(ui)
    c.open()
    c.sendcmd("009 ;get the matrix")
    c.close()
    """
    _errPat = re.compile(".*error:.*", re.I | re.DOTALL)
    _fnPat = re.compile('(.+)\.txt$', re.I)
    String_2_Byte = lambda a: bytearray([ord(s) for s in a])
    Byte_2_String = lambda a: "".join([chr(i) for i in a if i != 13])
    Is_Result_Error = lambda a: Controller._errPat.search(a)
    
    _introMsg ="""
;-------------
; File: %s, Created on: %s UTC
;-----------------
"""
    _timeFmt =  '%Y%m%d, %H:%M:%S'

    

    def __init__(self, ui):  # get the port id and the logging file ids
        """__init__(ui)

        ui is a UserInput object that has defined a file name as input and a
        serial port to be opened to the controller
        
        If the ui.inputfn is blank, then the defualt file name of test.txt will be used
        """
        ifn = ui.inputfn.strip()
        if not ifn: ifn = 'test.txt'
         
        m = Controller._fnPat.search(ifn)
        filename = m.group(1)
        self.cLfn = filename + '.cmdlog.txt'
        self.cEfn = filename + '.exelog.txt'        
        self.sp = ui.serial_port
        self.isFilesOpen = False
        self.isOpen = False
        self.ui = ui
        self.cmd = ""
        self.lastResponse = ""
        self.lastCmd = ""
        self.lastDisplayed = ""
        self.lastLogged = ""

    def __str__(self):
        return '[Controller: %s]' % (str(self.isFilesOpen) + ", " +
        str(self.isOpen) + ', ' + str(self.ui))

    def __repr__(self):
        return '[Controller: %s]' % (str(self.sp.isOpen()) + ', ' +
        str(self.isFilesOpen) +
        ", " + str(self.isOpen) + ', ' + str(self.ui))


    def open(self):
        """open()

        opens the controller, the serial port and the logging files
        sets isFilesOpen if logging files opened correctly
        sets isOpen if the Controller opened correctly
        
        returns True if the controller opened (both the files and the serial port), false
        otherwise
        """
        if self.sp.isOpen():
            self.sp.close()
        self.isFilesOpen = False
        result = False
        try:
            cLPathS = path.abspath(self.cLfn)
            cEPathS = path.abspath(self.cEfn)
            self.cLFile = open(self.cLfn, 'w', encoding='utf-8')
            self.cEFile = open(self.cEfn, 'w', encoding='utf-8')
            self.whenOpened = datetime.now().strftime(Controller._timeFmt)
            self.openTime = time()
            self.cLFile.write(Controller._introMsg % (cLPathS, self.whenOpened ))
            self.cEFile.write(Controller._introMsg % (cEPathS, self.whenOpened ))
            self.isFilesOpen = True
            self.sp.open()
            self.isOpen = True  
            result = True
        except:
            e = sys.exc_info()[0]
            result = False
            self.isOpen = False
            print("controller did not open! %s\n" % e)            
        
        return result


    def sendcmd(self, cmdin,
        display = True,
        logIt = True,
        echoit = False, 
        selectIt = lambda a: True, 
        formatIt = lambda a: (a, {})):        
        """sendcmd(cmd, display=TF, logIt=TF

        Logs the command as provided in the execution log with the results
        of the command.
        It removes the comments and spaces from the command so that it only
        sends the necessisary data.
        blank commands are ignored.

        Sends the command through the serial port and waits for the
        controller response.

        If display is True, the command and the controllers response is printed
        If logIt is True, the commands and the responses are logged
        (subject to selectIt)
        selectIt is a lambda that if it returns true, will cause the
         response to be logged.
         
           A typlical use of selectIt is: 1) TBD
         
        formatIt is a lambda that formats the response before logging it

      

        returns a True if command executed ok, false otherwise
        """
       
        result = True  
        cmd = ""
        if type(cmdin) is bytes:
            cmd = Byte_2_String(cmdin)
        else:
            cmd = cmdin

        #print(cmd) # display command on window
        if logIt:
            self.cLFile.write(cmd + "\n")  # write to command log file
            self.cEFile.write(cmd + "\n")  # write to execution log file

        sansComment = cmd.split('\n', 1)  # remove trailing new line
        sansComment = sansComment[0].split(';', 1)  # remove trailing comment
        necmd = sansComment[0].split()  # split on spaces

        if len(''.join(necmd).strip()) == 0:  # ignore blank lines
            self.lastCmd = ""
            return result

        else:
            String_2_Byte =  Controller.String_2_Byte
            Byte_2_String =  Controller.Byte_2_String
            #print(''.join(necmd)+"\n")
            necmd.append('\r')  # add a new line
            newcmd = ''.join(necmd)
            self.lastCmd = newcmd
            if not echoit:               
                self.sp.flushInput()  # deprecated, use reset_input_buffer()
                #print(newcmd)
                sto = self.sp.timeout  # speed up the reads
                self.sp.timeout = 0.2
                byts = String_2_Byte(newcmd)
                self.sp.write(byts)
                #self.sp.write(String_2_Byte(newcmd))
                inList = []
                cnt = 100
                while cnt > 0:  # keep reading input until the DTMF> prompt is seen.
                               # Remember the timeout changes with baud rate
                    #should get data atleast every timeout seconds
                    inList.append(Byte_2_String(self.sp.dread(9999)))
                    cnt = cnt - 1
                    if ''.join(inList).endswith('DTMF>'):
                        break
    
                # rnok = self.__resultNotOk__(''.join(inList))
                self.sp.timeout = sto
                rnok = Controller.Is_Result_Error(''.join(inList))
                if rnok:
                    inList.append("******************E R R O R" +
                    "****************\nDTMF>")
                    result = False
                response = ''.join(inList)
            else:
                response = newcmd
                
            self.lastResponse = response
            if display:
                self.lastDisplayed = response
                print(response)
            if logIt and selectIt(response):
                self.lastLogged = response
                self.cEFile.write(formatIt(response)[0])
        return result

    def close(self):
        """close()

        Closes the controller, the logging files, and the serial port
        """       
        if self.sp.isOpen():
            self.sp.close()
        self.isOpen = False
        if self.isFilesOpen:
            try:
                self.cLFile.close()
            except: pass
            try:
                self.cEFile.close()
            except: pass            
            self.isFilesOpen = False

if __name__ == '__main__':
    ui = userinput.UserInput()
    try:    
        def _cmdloop(c):
            print("Quit or Exit to exit command mode")
            while True:        
                cmd = input("input>")
                cmd = cmd.strip().upper()
                if cmd.startswith('Q') or cmd.startswith('E'):
                    print("Exiting command input mode...")
                    break
                c.sendcmd(cmd)
        
        def sendUsersCmds():
            global ui
            ui.open()
            c = Controller(ui)
            c.open()
            try:
                _cmdloop(c)
                c.close()        
            finally:
                if ui.serial_port.isOpen():ui.serial_port.close()
                c.close()
        
        print('Available comport(s) are: %s' % getports.GetPorts().get())       

        ui.request()
        sendUsersCmds()
        ui.close()
       
    except(Exception, KeyboardInterrupt) as exc:
        ui.close()
        sys.exit(exc)
        