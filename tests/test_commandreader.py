#!/usr/bin/env python3
"""
Test file for commandreader
"""
from __future__ import print_function
import sys
import unittest

from commandreader import CommandReader
import userinput
import knowncontrollers
import dlxii


def eprint(*args, **kwargs):
    """eprint(*args, **kwards)

    force a print to sys.stderr
    """
    print(*args, file=sys.stderr, **kwargs)


class TestCommandreader(unittest.TestCase):
    """command reader test"""
    ctrl = knowncontrollers.select_controller('dlxii')[1]
    ui = userinput.UserInput(ctrl)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @classmethod
    def setUpClass(cls):
        TestCommandreader.ui.inputfn = "cmdreadertest.txt"

    @classmethod
    def tearDownClass(cls):
        pass

    def test0_inst(self):
        _cr = CommandReader(TestCommandreader.ui)
        eres = '[CommandReader closed: True, [UserInput: , cmdreadertest.txt]]'
        self.assertEqual(eres, str(_cr))
        self.assertEqual(eres, repr(_cr))

    def test1_open(self):
        """testopen()

        """
        _cr = CommandReader(TestCommandreader.ui)
        _fcr = None
        try:
            self.assertTrue(_cr.atts['is_closed'])
            self.assertEqual("", _cr.get())
            _cr.close()
            self.assertTrue(_cr.open())

            eres = '[CommandReader closed: False, [UserInput: , cmdreadertest.txt]]'
            self.assertEqual(eres, str(_cr))
            self.assertEqual(eres, repr(_cr))

            self.assertFalse(_cr.atts['is_closed'])
            try:
                _cr.open()
                assert "did not detect multiple attempts to open"
            except AssertionError:
                pass

            _cr.close()
            self.assertTrue(_cr.atts['is_closed'])
            fakeui = userinput.UserInput(dlxii.Device())
            fakeui.inputfn = 'totaljunk.txt'
            _fcr = CommandReader(fakeui)
            self.assertFalse(_fcr.open())
            self.assertEqual("[Errno 2] No such file or directory: 'totaljunk.txt'",
                             str(_fcr.atts['lasterror']))
            self.assertTrue(_fcr.atts['is_closed'])
        finally:
            if _fcr:
                _fcr.close()

            _cr.close()

    def test0_close(self):
        """"check for close working"""
        _cr = CommandReader(TestCommandreader.ui)
        if (_cr.atts['is_closed']):
            _cr.open()
        self.assertFalse(_cr.atts['is_closed'])
        _cr.close()
        self.assertTrue(_cr.atts['is_closed'])

    def test3_get(self):
        """testget

        """
        _cr = CommandReader(TestCommandreader.ui)
        try:
            _cr.open()
            lines = []

            while True:
                line = _cr.get()
                if line == "":
                    break
                lines.append(line)

            # should have read all lines from a stream so the stream should automatically
            # close
            self.assertTrue(_cr.atts['is_closed'])
            self.assertEqual(7, len(lines))
            lastline = lines[6]
            self.assertFalse(lastline.endswith("\n"))
            emptyline = lines[5]
            self.assertEqual("\n", emptyline)
            self.assertEqual("line 4\n", lines[3])

        finally:
            _cr.close()
            self.assertTrue(_cr.atts['is_closed'])


if __name__ == '__main__':
    unittest.main()
