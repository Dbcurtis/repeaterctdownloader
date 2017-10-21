#!/usr/bin/env python3
import os
import sys
import serial

class MySerial(serial.Serial): 
    
    _debugging = False
    
    _debugreturns =  [b'ok\nDTMF>']
    _dbidx=0
     
    
    Byte_2_String = lambda bs:"".join([chr(int(b)) for b in bs if int(b)!=13])    
    """Byte_2_String(bs)
    
    Takes a byte array (bs) and returns the corrosponding string
    """
    
    String_2_Byte = lambda st: bytes([ord(s) for s in st])
    """String_2_Byte(st)
    
    Takes a string (st) and returns a corrosponding byte array
    """    
    def __init__(self, controllerInfo):
        super(serial.Serial,self).__init__()
        self.controllerInfo=controllerInfo
        
    def __str__(self):
        aa =  super(serial.Serial,self).__str__()
        return "testing:" + str(MySerial._debugging) + ", " + aa
          
    
    def dread(self,numchar):
        global __debugging
        if not MySerial._debugging:return self.read(numchar)
        else: 
            result =  MySerial._debugreturns[MySerial._dbidx]
            MySerial._dbidx+=1
            return result
        
    def spOK(self):  # assume the sp is open
        """spOK()
    
        Checks to see if an open serial port is communicating with the controller
    
        Writes a \r to the serial port and reads the result
        If the result ends with DTMF> the port and repeater are communicating
        
        Returns True if communicating, False if not
        """
        sp=self
        sp.flushInput()
        sp.close()
        to=sp.timeout
        sp.timeout= 0.25 + (110.0/sp.baudrate)
        sp.open()
        sp.dread(9999)
        sp.write(MySerial.String_2_Byte('\r'))
        """ will generate some response
        ending in DTMF> if the cps rate is correct
        """
        ctrlresult = MySerial.Byte_2_String(sp.dread(9999))
        #print(ctrlresult)
        #sp.timeout = to
        sp.close()
        sp.timeout=to
        sp.open()
        return ctrlresult.endswith("DTMF>")        
        
    def findBaudRate(self):
        """findBaudRate()
    
        ui is a UserInput object
        Attempts to communicate to the repeater controller using speeds
        9600,19200,4800,1200,600,300.
        The first attempt that works (see spOK) will be selected to be the
        speed for the serial port.
        There is some attempt to adjust the wait serial port timeouts
        responsive to the baud rate.
        My current belief is that the wait is not that importaint, but have
        not yet tried anything other than 9600
    
        If the baud rate cannot be determined, the sp is returned to
        the state it was on entry.
    
        side-effects
        If the serial port is open on entry, it will be open on exit,
        otherwise it is closed.
    
        returns True if a matching baud rate is found, otherwise returns False
        """
        sp=self
        ci=self.controllerInfo
        No = -1      
        spOpen = sp.isOpen()
        if not spOpen: sp.open()
            
      #  if spOpen:  # if open port, and it is communicating just return the baudrate
        if self.spOK():
            if not spOpen:sp.close()
            return True
        sp.flushInput()
        sp.close()  # if open and not communicating the port is closed
    
        savedbr = sp.baudrate
        savedto = sp.timeout
    
        scps = No  # setup for storing the selected baud rate and timeout
        sto = 0.0
        # at this point the serial port is always closed
        for cpsd in ci.cpsData:
            sp.baudrate = cpsd.bps
            sp.timeout = cpsd.cpsDelay
            cnt = 2
            print("trying " + str(cpsd.bps) + " baud")
            while cnt > 0:
              #  print("acnt: "+str(cnt)+", "+str(sp))
                sp.open()  # try these settings
                if not self.spOK():
                    cnt = cnt - 1
                    sp.close()
                else:
                    scps = cpsd.bps  # setting worked, so save and break the loop
                    sto = cpsd.cpsDelay
                    #print("found one");
                    #print(str(sp))                    
                    sp.close()
                    cnt = -10
                    break
              
            if cnt < -9:
                break
    
        #print("scps: "+str(scps));
        if sp.isOpen():
            sp.close()  # close the serial port if still open
        
        result = False    
        if scps == No:
            sp.baudrate = savedbr  # no match found, just restore port
            sp.timeout = savedto
            result = False  # show fail
        else:
            sp.baudrate = scps  # match found, set the baud rate and timeout
            sp.timeout = sto
            result = True  # show ok
            
        if spOpen:  # restore the open closed state; port is currently closed
            sp.open()
            sp.flushInput() 
        return result
    
    
if __name__ == '__main__':
    pass
   