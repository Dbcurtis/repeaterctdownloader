#!/usr/bin/env python3
import os
import sys
import userinput

class CommandReader:
    """CommandReader

    cr = CommandReader(ui)
    where ui is a UserInput object.

    This class reads commands from a file.
    Those commands can be sent to Controller.sendcmd for execution
    """

    def __init__(self, ui):
        self.ui = ui
        self.line = ""
        self.isClosed = True
        self.loc = -1  # loc is used to keep track of when the read is done
        self.fn = ui.inputfn
        self.lasterror = None
        
    def __str__(self):
        return '[CommandReader %s]' % ('closed: '+str(self.isClosed) +  ", "+str(self.ui))

    def __repr__(self):
        return '[CommandReader %s]' % ('closed: '+str(self.isClosed) +  ", "+str(self.ui))      

    def open(self):
        """open()

        Opens the input file from the UserInput
        returns true if the file is opened, false otherwise
        
        If the reader is already open when called, will throw an assertion error
        """
        
        result = False
        if not self.isClosed:raise AssertionError('Commandreader already open, aborting...')
        #assert(self.closed,'Commandreader already open, aborting...')
        try:
            self.f = open(self.fn, "r")  # assuming file exists and is readable
            self.isClosed = False
            self.lasterror=None
            result=True
        except FileNotFoundError as e:
            print(e)
            self.lasterror=e
            self.isClosed = True
        return result

    def get(self):  # line returns line or "" if EOF
        """get()

        Gets the next line from the input file
        if the file is closed, the returned line is ""
        """
        
        if self.isClosed:
            return ""
       
        try:
            self.line = self.f.readline()
            idx = self.f.tell()
            if idx == self.loc:
                self.isClosed = True
                return ""
            self.loc = idx
            return self.line
        
        except EOFerror:
            self.isClosed = True
           
    def close(self):
        """close()

        Closes the input file and the reader
        Can be called multiple times.
        """
        
        if not self.isClosed:          
            self.isClosed = True
            try:
                self.f.close()
            except:
                pass
            
            
if __name__ == '__main__':
    """Main
    
    opens a UI, opens a CommandReader
    Reads the imput file and dumps to the terminal
    """
    ui = userinput.UserInput()
    ui.request()
    ui.open(detectBR= False)
    cr = CommandReader(ui)
    try:       
        cr.open()
        while True:
            line = cr.get()
            if not line:
                break
            jj = line.split('\n')
            print(jj[0])
    finally:
        cr.close()
        ui.close()
        
    
