#!/usr/bin/env python3
"""Module DocString TBD"""

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
        self.is_closed = True
        self.loc = -1  # loc is used to keep track of when the read is done
        self.file_name = ui.inputfn
        self.lasterror = None
        self.file_in = None

    def __str__(self):
        return '[CommandReader %s]' % ('closed: '+str(self.is_closed) +  ", "+str(self.ui))

    def __repr__(self):
        return '[CommandReader %s]' % ('closed: '+str(self.is_closed) +  ", "+str(self.ui))

    def open(self):
        """open()

        Opens the input file from the UserInput
        returns true if the file is opened, false otherwise

        If the reader is already open when called, will throw an assertion error
        """

        result = False
        if not self.is_closed:
            raise AssertionError('Commandreader already open, aborting...')
        #assert(self.closed,'Commandreader already open, aborting...')
        try:
            self.file_in = open(self.file_name, "r")  # assuming file exists and is readable
            self.is_closed = False
            self.lasterror = None
            result = True
            self.loc = -1
        except FileNotFoundError as _e:
            print(_e)
            self.lasterror = _e
            self.is_closed = True
        return result

    def get(self):  # line returns line or "" if EOF
        """get()

        Gets the next line from the input file
        if the file is closed, the returned line is ""
        """

        if self.is_closed:
            return ""

        try:
            self.line = self.file_in.readline()
            idx = self.file_in.tell()
            if idx == self.loc:
                self.is_closed = True
                return ""
            self.loc = idx
            return self.line

        except EOFError:
            self.is_closed = True

    def close(self):
        """close()

        Closes the input file and the reader
        Can be called multiple times.
        """

        if not self.is_closed:
            self.is_closed = True
            try:
                self.file_in.close()
                self.loc = -1
            except IOError:
                pass


def __main():
    """__main()

    gets user input, opens port to the repeater, sends the contents of the specified file
    to the repeater controller, closes down
    """
    _ui = userinput.UserInput()
    _ui.request()
    _ui.open(detect_br=False)
    _cr = CommandReader(_ui)
    try:
        _cr.open()
        while True:
            line = _cr.get()
            if not line:
                break
            _jj = line.split('\n')
            print(_jj[0])
    finally:
        _cr.close()
        _ui.close()

if __name__ == '__main__':
    __main()
