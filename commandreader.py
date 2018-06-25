#!/usr/bin/env python3
"""Module commandreader.py


"""
import os
import logging
import logging.handlers
import userinput

LOGGER = logging.getLogger(__name__)

LOG_DIR = os.path.dirname(os.path.abspath(__file__)) + '/logs'
LOG_FILE = '/commandreader'


def _donothing():
    pass

class CommandReader:
    """CommandReader

    cr = CommandReader(ui)
    where ui is a UserInput object.

    This class reads commands from a file.
    Those commands can be sent to Controller.sendcmd for execution
    """

    def _setclosed(self):
        #self.is_closed = True
        self.atts['is_closed'] = True
        try:
            self.atts['file_in'].close()
            self.loc = -1
        except IOError:
            pass

    def __init__(self, _ui):
        self.atts = {'lasterror': None, "file_in": None,
                     'file_name': _ui.inputfn, 'line': "", 'is_closed': True,}

        self.ui = _ui
        self.loc = -1  # loc is used to keep track of when the read is done
        self._set_closed_ifd = {
            True: _donothing,
            False: self._setclosed,
        }

    def __str__(self):
        return '[CommandReader closed: {}, {}]'.format(str(self.atts['is_closed']), str(self.ui))

    def __repr__(self):
        return '[CommandReader closed: {}, {}]'.format(str(self.atts['is_closed']), str(self.ui))

    def open(self):
        """open()

        Opens the input file from the UserInput
        returns true if the file is opened, false otherwise

        If the reader is already open when called, will throw an assertion error
        """

        result = False
        if not self.atts['is_closed']:
            raise AssertionError('Commandreader already open, aborting...')
        #assert(self.closed,'Commandreader already open, aborting...')
        try:
            self.atts['file_in'] = open(
                self.atts['file_name'], "r")  # assuming file exists and is readable
            self.atts['is_closed'] = False
            self.atts['lasterror'] = None
            result = True
            self.loc = -1

        except FileNotFoundError as _e:
            print(_e)
            self.atts['lasterror'] = _e
            self.atts['is_closed'] = True

        return result

    def get(self):
        """get()

        Gets the next line from the input file
        if the file is closed or EOF, the returned line is ""
        """

        if self.atts['is_closed']:
            return ""

        try:
            self.atts['line'] = self.atts['file_in'].readline()
            idx = self.atts['file_in'].tell()
            if idx == self.loc:
                self.atts['is_closed'] = True
                return ""
            self.loc = idx
            return self.atts['line']

        except EOFError:
            self.atts['is_closed'] = True
            return ""


    def close(self):
        """close()

        Closes the input file and the reader
        Can be called multiple times.
        """
        self._set_closed_ifd.get(self.atts['is_closed'])()


def __main():
    """__main()

    gets user input, opens port to the repeater, sends the contents of the specified file
    to the repeater controller, closes down
    """
    if not os.path.isdir(LOG_DIR):
        os.mkdir(LOG_DIR)
    LF_HANDLER = logging.handlers.RotatingFileHandler(
        ''.join([LOG_DIR, LOG_FILE, ]),
        maxBytes=10000,
        backupCount=5,
        )
    LF_HANDLER.setLevel(logging.DEBUG)
    LC_HANDLER = logging.StreamHandler()
    LC_HANDLER.setLevel(logging.DEBUG)  #(logging.ERROR)
    LF_FORMATTER = logging.Formatter(
        '%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s')
    LC_FORMATTER = logging.Formatter('%(name)s: %(levelname)s - %(message)s')
    LC_HANDLER.setFormatter(LC_FORMATTER)
    LF_HANDLER.setFormatter(LF_FORMATTER)
    THE_LOGGER = logging.getLogger()
    THE_LOGGER.setLevel(logging.DEBUG)
    THE_LOGGER.addHandler(LF_HANDLER)
    THE_LOGGER.addHandler(LC_HANDLER)
    THE_LOGGER.info('commandreader executed as main')
    #LOGGER.setLevel(logging.DEBUG)
    _ui = userinput.UserInput()
    _ui.request()
    _ui.open(detect_br=False)
    _cr = CommandReader(_ui)
    try:
        _cr.open()
        while 1:
            _line = _cr.get()
            if not _line:
                break
            _jj = _line.split('\n')
            print(_jj[0])
    finally:
        _cr.close()
        _ui.close()

if __name__ == '__main__':
    __main()
