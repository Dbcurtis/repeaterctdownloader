#!/usr/bin/env python3
"""This script prompts for user input for serial port etc."""
import sys
import myserial
import getports
import knowncontrollers
import dlxii


class UserInput:
    """UserInput()

    obtains user input for which serial port to use and a path for
    an input file to be read.

    if run as __main__

    Displays available prots,
    Obtains user input for the selected port and file (the file info is ignored)
    Attempts to open the port, and if able prints "Requested Port can be opened"
    May also generate an OSError if unable to match the controller baud rate

    """
    @classmethod
    def __ignore(cls, a):
        pass

    __close_ifd = {True: lambda a: a.close(), False: lambda a: UserInput.__ignore(a),}
    __userInput_ifd = {
        True: lambda o, a: UserInput.__popTestData(o, a),
        False: lambda o, a: UserInput.__inputg(o, a),}    
    
    @staticmethod 
    def __popTestData(o, a):
        return o.__td.pop()
    
    @staticmethod 
    def __inputg(o, a):
        return input(a)
    
  
    def __init__(self, ctype=dlxii.DlxII(), testdata=None):
        self.comm_port = ""
        self.inputfn = ""
        self.controller_type = ctype
        self.serial_port = myserial.MySerial(self.controller_type)
        self.__td = None
        if testdata:
            if isinstance(testdata, list):
                self.__td = testdata
                self.__td.reverse()
            else:
                assert "illegal testdata type"

    def __str__(self):
        return '[UserInput: %s]' % (self.comm_port + ", " + self.inputfn)

    def __repr__(self):
        return '[UserInput: %s]' % (self.comm_port + ", " + self.inputfn)

    def __inputa(self, query):
        return UserInput.__userInput_ifd.get(isinstance(self.__td, list))(self, query)

    def request(self):
        """request()

        Request comm port id and filename containing controller commands
        """
        while 1:
            available = getports.GetPorts().get()
            #print('available ports:'+', '.join(available))
            print('Available comport(s) are: %s' % available)
            tups = [(a.strip(), a.strip().lower()) for a in available]
            useri = self.__inputa("Comm Port for repeater?>").strip()
            hits = [t for t in tups if useri.lower() in t]
            if hits:
                [_port] = hits
                self.comm_port = _port[0]
                print('Using serial port: %s' % self.comm_port)
                break

        print('Known controlers: \n\t'
              +'\n\t'.join(knowncontrollers.KnownControllers.get_controller_ids()))

        _msg = 'Controler options: ' + str(knowncontrollers.KnownControllers.get_known())
        while 1:
            print(_msg)
            useri = self.__inputa("Controller type?>")
            ctrl = knowncontrollers.KnownControllers.select_controller(useri)
            if ctrl:
                self.controller_type = ctrl
                self.serial_port = myserial.MySerial(self.controller_type)
                break

        self.inputfn = self.__inputa("file name to send to repeater or blank?>")

    def close(self):
        """close()

        Closes the serial port if it is open
        """
        UserInput.__close_ifd.get(self.serial_port.isOpen())(self.serial_port)


    def open(self, detect_br=True):
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
        sport = self.serial_port
        try:
            sport.port = self.comm_port  # '/dev/ttyACM0'
            sport.timeout = .2
            sport.baudrate = 9600
            if sport.isOpen():
                sport.close()
            sport.open()

        except myserial.serial.SerialException as sex:
            self.comm_port = ""
            print(sex)
            return False

        if detect_br:
            if not sport.find_baud_rate():
                raise OSError('Unable to match controller baud rate')
        return True

if __name__ == '__main__':
    UI = UserInput()
    try:
        UI.request()
        UI.open()
        print("Requested Port can be opened")
        UI.close()
    except(Exception, KeyboardInterrupt) as exc:
        UI.close()
        sys.exit(str(exc))
