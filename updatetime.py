#!/usr/bin/env python3
"""This script updates the repeater's time and date"""
import sys
import os
#from typing import Any, Union, Tuple, Callable, TypeVar, Generic, Sequence, Mapping, List, Dict, Set, Deque, Iterable
from typing import Any, Union, Tuple, Callable, TypeVar, Generic, Sequence, Mapping, List, Dict, Set, Deque, Iterable
import time
import datetime
import logging
import logging.handlers
import knowncontrollers
import controller
import userinput
import getports
from updatetime_aux import _no_op, _delay, check_date, check_time,  \
    SET_ATTEMPT_MAX, INST, PAT, REPL_FMT, _PARSER


CLOSER = {False: lambda a: a.close(), True: lambda a: _no_op(a)}

LOGGER = logging.getLogger(__name__)

LOG_DIR = os.path.dirname(os.path.abspath(__file__)) + '/logs'
LOG_FILE = '/updatetime'


def help_processing(_available_ports, tempargs):
    """tbd"""
    if not ('-h' in tempargs or '--help' in tempargs):
        if not _available_ports:
            msg = 'no available communication port: aborting'
            raise SystemExit(msg)
    if '-h' in tempargs or '--help' in tempargs:
        _PARSER.print_help()
        raise SystemExit()


def process_cmdline(_available_ports: List[str], _testcmdline=None):
    """process_cmdline(_available_ports, _testcmdline="")

    _available_ports is a list? of port names
    _testcmdline can be list of strings that can be used to fake a command line.
    If None, the default
    command line processing is performed, otherwise,
    the list of strings in the argument is used.

    processes the command line arguments
    returns a tuple of (ui, verbose, cmdl_debug) if arguments are ok, Otherwise raises an exception
    """
    msg: str = ''
    _tcl = []
    if _testcmdline:
        _tcl = _testcmdline
    tempargs = sys.argv[1:] + _tcl
    help_processing(_available_ports, tempargs)

    if _testcmdline:
        args = _PARSER.parse_args(_testcmdline)
    else:
        args = _PARSER.parse_args()

    if args.logdebug:
        LOGGER.setLevel(logging.DEBUG)
    elif args.loginfo:
        LOGGER.setLevel(logging.INFO)

    possible_port: str = args.Port
    if args.Controller:
        possible_ctrl = args.Controller
    else:
        possible_ctrl = 'dlxii'

    if len(_available_ports) != 1:
        if not args.Port.upper() in _available_ports:
            msg = f'Port {args.Port} not available: available ports are: {_available_ports}, aborting'

            raise Exception(msg)
    else:
        possible_port = _available_ports[0]

    ctrl: Tuple[str, Any] = knowncontrollers.select_controller(possible_ctrl)
    if not ctrl:
        msg = f'Controller {args.Controller} not available: available controlers are: {knowncontrollers.get_controller_ids()}, aborting'

        raise Exception(msg)

    verbose: bool = args.verbose
    cmdl_debug = args.cldebug
    _ui = userinput.UserInput(ctrl[1])
    _ui.comm_port = possible_port
    if verbose:
        msg = f'[verbose] ctrl:{ctrl}, port:{_ui.comm_port}, dbg:{cmdl_debug}, verbose: True'

    return (_ui, verbose, cmdl_debug)


class Stuff:
    """Stuff

    """

    def __init__(self, uiintuple):
        self._ui = uiintuple[0]
        self.verbose = uiintuple[1]
        self.cmdl_debug = uiintuple[2]
        self._ct = None
        _delay()

    def _helper1(self, cmd: str, msg: str):

        if not self.cmdl_debug:
            if cmd and not self._ct.sendcmd(cmd, display=self.verbose or self.cmdl_debug):
                raise ValueError(f'retry {msg} command send error')
        else:
            print(f'debugging, would have set {msg} with {cmd}')

# -----------------------------
    def settime(self, _the_time, debug_time) -> str:
        """settime()

        checks to see if the times are different,
        and if so, generates and executes a command
        to the controller

        returns with the command if a command was needed,
        or None if no time change was required
        if command error raises ValueError("retry date command send error")
        """
        cmd = None
        ctrl = self._ct.ui.controller_type
        gttpl = ctrl.newcmd_dict['gtime']
        sttpl = ctrl.newcmd_dict['stime']
        _the_time[True] = time.localtime(time.time())
        if self._ct.sendcmd(gttpl[INST], self.cmdl_debug or self.verbose):
            _res = gttpl[REPL_FMT](gttpl[PAT].search(
                self._ct.atts['last_response']))
            systime = _the_time.get(debug_time is None)
            if self.verbose:
                print(self._ct.atts['last_response'])
            cmd = check_time(_res, sttpl, systime)
            self._helper1(cmd, 'time')
        return cmd

# -------------------------

    def setdate(self, _the_time, debug_time):
        """setdate()

        checks to see if the dates are different, and if so,
        generates and executes a command
        to the controller

        returns with the command if a command was needed,
        or None if no date change was required

        if command error, raises ValueError("retry date command send error")
        """

        ctrl = self._ct.ui.controller_type
        gdtpl = ctrl.newcmd_dict['gdate']
        sdtpl = ctrl.newcmd_dict['sdate']
        cmd = None
        _the_time[True] = time.localtime(time.time())
        if self._ct.sendcmd(gdtpl[INST], self.cmdl_debug or self.verbose):
            systime = _the_time.get(debug_time is None)
            cmd = check_date(gdtpl[REPL_FMT](gdtpl[PAT].search(self._ct.atts['last_response'])),
                             sdtpl, systime)
            self._helper1(cmd, 'date')
            if self.verbose:
                print(self._ct.atts['last_response'])
                print(time.localtime(time.time()))

        return cmd

    def doit(self, debug_time=None) -> Tuple[Any, ...]:
        """doit(_debug_time=)

        does all the work
        _ui is the UserInput

        returns    (cntdown, succ, noneed) which is the countdown, if successful, if not needed

        """

        # cmdl_debug = self.cmdl_debug
        result: Tuple[Any, ...] = ()
        _the_time: Dict[bool, Any] = {
            False: debug_time, True: time.localtime(time.time()), }
        try:
            _ui = self._ui
            _ui.open()
            self._ct = controller.Controller(_ui)
            self._ct.open()

            # ctrl = self._ct.ui.controller_type
            cntdown = SET_ATTEMPT_MAX  # fifteen attempts max
            while cntdown > 0:
                cntdown -= 1
                try:

                    # check the dates are the same and if not make them so
                    if self.setdate(_the_time, debug_time):
                        LOGGER.info("date changed")
                        if self.verbose:
                            print('date change, try again')
                        continue  # made a change, try again

                    if not self.settime(_the_time, debug_time):
                        break
                    LOGGER.info("time changed")
                    if self.verbose:
                        print('time change, try again')

                except Exception as _ve:  # do not really know what I am trying to catch here
                    # shurly ValueError, but what others?
                    LOGGER.debug("10 second sleep")
                    time.sleep(10)  # 10 sec sleep
                    print(_ve.args)

            succ = cntdown > 0
            if self.verbose:
                print(f'cntdown: {countdown}')  # .format(cntdown))

            noneed = cntdown == SET_ATTEMPT_MAX - 1
            result = (cntdown, succ, noneed)
            if self.verbose:
                ifa: Dict[bool, str] = {
                    True: 'Controller date-time was current', }
                ifa[False] = f'Controller time sucessfully set: {succ}'
                print(
                    ' '.join([str(datetime.datetime.now()), ifa.get(noneed), ]))

            self._ct.close()
            self._ui.close()

        finally:
            CLOSER.get(self._ct is None)(self._ct)
            CLOSER.get(self._ui is None)(self._ui)

        return result


def main():
    """main()

    gets the port and repeater type from the command line arguments,
    reads the time and date from the controller
    reads the time from the opsys
    if it is close to a day change (within 10 min) Will delay until after the day change

    compares them and if more than 60 seconds difference updates the time on the controller
    """

    print(time.asctime(time.localtime(time.time())))
    stuff = Stuff(process_cmdline(getports.GetPorts().get()))
    result = stuff.doit()
    print(result)


if __name__ == '__main__':

    if not os.path.isdir(LOG_DIR):
        os.mkdir(LOG_DIR)
    LF_HANDLER = logging.handlers.RotatingFileHandler(
        ''.join([LOG_DIR, LOG_FILE, ]),
        maxBytes=10000,
        backupCount=5,
    )
    LF_HANDLER.setLevel(logging.DEBUG)
    LC_HANDLER = logging.StreamHandler()
    LC_HANDLER.setLevel(logging.DEBUG)  # (logging.ERROR)
    LF_FORMATTER = logging.Formatter(
        '%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s')
    LC_FORMATTER = logging.Formatter('%(name)s: %(levelname)s - %(message)s')
    LC_HANDLER.setFormatter(LC_FORMATTER)
    LF_HANDLER.setFormatter(LF_FORMATTER)
    THE_LOGGER = logging.getLogger()
    THE_LOGGER.setLevel(logging.DEBUG)
    THE_LOGGER.addHandler(LF_HANDLER)
    THE_LOGGER.addHandler(LC_HANDLER)
    THE_LOGGER.info('updatetime executed as main')
    # LOGGER.setLevel(logging.DEBUG)

    try:
        main()
    except SystemExit as sex:
        print(sex)
    except(Exception, KeyboardInterrupt) as exc:
        print(str(exc))
        sys.exit(str(exc))
