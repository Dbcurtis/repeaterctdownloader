#!/usr/bin/env python3
"""This script updates the repeater's time and date"""
import sys
import argparse
import time
import logging
import logging.handlers
import userinput
import knowncontrollers
import controllerspecific

HOURLIM = 23
MINLIM = 50
O_DOW = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'foolsday']
R_DOW = [7, 6, 0, 1, 2, 3, 4, 5, ]
M_DOW = ['2', '3', '4', '5', '6', '7', '1', ]

TWO_CHAR = '{num:02d}'
SET_ATTEMPT_MAX = 15

INST = controllerspecific.INST
PAT = controllerspecific.PAT
REPL_FMT = controllerspecific.REPL_FMT

_PARSER = argparse.ArgumentParser(description="Sets a controller's date and time if \
needed: a blank argument assumes dlx2 and one available com port",
                                  epilog="Useful for running in a cron job"
                                  )
_PARSER.add_argument('Controller', default=None,
                     help='Controller type, one of [dlx2, rlc1+] required unless no arguments'
                     )
_PARSER.add_argument('Port', nargs='?', default=None,
                     help='Port id if required, if only one open port, that one will be used'
                     )
_PARSER.add_argument('-dbg', '--cldebug',
                     help='turns off setting the new time',
                     action="store_true")
_PARSER.add_argument('-v', '--verbose',
                     help='display detailed messages',
                     action="store_true")
_PARSER.add_argument('-li', '--loginfo',
                     help='enable INFO logging',
                     action="store_true")
_PARSER.add_argument('-ld', '--logdebug',
                     help='enable DEBUG logging',
                     action="store_true")


def _no_op(ignore):
    # pylint: disable=W0613
    pass

CLOSER = {False: lambda a: a.close(), True: lambda a: _no_op(a)}

#cmdl_debug = False
#verbose = False

LOGGER = logging.getLogger(__name__)
LOG_DIR = '../logs'
LOG_FILE = '/updatetime'


def _delay(debug=False, testtime=None):
    """_delay()

    if the time is >23:50, waits until 2 seconds after the date changes before continuing

    after the delay, returns a tuple with the then current time and a debug message. if
    debugging is false the debugging message is None
    """

    while 1:
        msg = None

        os_time = time.localtime(time.time())
        if testtime:
            os_time = testtime
        if os_time.tm_hour < HOURLIM or os_time.tm_min < MINLIM:
            break

        delymin = 60 - os_time.tm_min  #- MINLIM
        LOGGER.debug("debug wait for %s min and 2 seconds", str(delymin))
        if debug:
            msg = 'debug wait for {} min and 2 seconds' .format(delymin)
            break
        else:

            time.sleep(delymin*60+2)
    return (time.localtime(time.time()), msg)

def check_date(_res, _sdtpl, _os_time):
    """check_date(_res,_sdtpl,_os_time)

    _res is the dict set by gdtpl[2] that has keys A, m, d, Y
    with the same meaning as https://docs.python.org/3.0/library/time.html

    _sdtpl is the set date tuple

    _os_time is the current computer time

    return None if the repeater date and the computer date match
    otherwise returns the command to set the repeater date.
    """
    # pylint: disable=C0103
    cmd = None
    dow = _res['A'].lower()
    _m = _res['m']
    _d = _res['d']
    _Y = _res['Y']

    _oY = str(_os_time.tm_year)
    _om = TWO_CHAR.format(num=_os_time.tm_mon)
    _od = TWO_CHAR.format(num=_os_time.tm_mday)
    _owd = _os_time.tm_wday
    textdow = O_DOW[_owd]
    #aa = M_DOW[_owd]
    if not (_Y == _oY and _d == _od and _m == _om and textdow == dow):
        arg = (_sdtpl[0], _om, _od, _oY[2:4], M_DOW[_owd], )
        cmd = _sdtpl[3](arg)
    LOGGER.debug("returned %s", cmd)
    return cmd


def check_time(_res, _sttpl, _os_time):
    """check_time(_res,_sttpl,_os_time)

    _res is the dict set by gttpl[2] that has keys I, M, p
    with the same meaning as https://docs.python.org/3.0/library/time.html

    _sttpl is the set time tuple

    _os_time is a time.struct_time with the current computer time

    return None if the repeater time and the computer time match
    otherwise returns the command to set the repeater time.
    """
    # pylint: disable=C0103
    cmd = None

    _I = _res['I']
    _M = _res['M']
    _p = _res['p']
    _pm = '0'
    if _p[0:1] == 'P':
        _pm = '1'
    _seconds = int(_M) * 60
    if _pm == '0':
        if int(_I) != 12:
            _seconds += int(_I) * 3600
    else:
        j = int(_I)
        if j != 12:
            j += 12
        _seconds += j * 3600

    _H = time.strftime("%H", time.gmtime(_seconds))
    _sysI = time.strftime("%I", _os_time)
    _sysH = TWO_CHAR.format(num=_os_time.tm_hour)
    _sysM = TWO_CHAR.format(num=_os_time.tm_min)
    _sysPM = '0'
    if int(_sysH) > 11:
        _sysPM = '1'

    if _H == _sysH and _M == _sysM and _pm == _sysPM:
        LOGGER.debug("returned %s", cmd)
        return cmd

    #now need to adjust

    arg = (_sttpl[0], _sysI, _sysM, _sysPM)
    cmd = _sttpl[3](arg)
    LOGGER.debug("returned %s", cmd)
    return cmd

def proc1(tempargs, _available_ports):
    """tbd"""
    if not ('-h' in tempargs or '--help' in tempargs):
        if _available_ports.isEmpty():
            msg = 'no available communication port: aborting'
            raise SystemExit(msg)
    if '-h' in tempargs or '--help' in tempargs:
        _PARSER.print_help()
        raise SystemExit()

def proc2(args):
    """tbd"""
    if args.logdebug:
        LOGGER.setLevel(logging.DEBUG)
    elif args.loginfo:
        LOGGER.setLevel(logging.INFO)

    possible_port = args.Port
    if args.Controller:
        possible_ctrl = args.Controller
    else:
        possible_ctrl = 'dlxii'
    return (possible_port, possible_ctrl, )

def process_cmdline(_available_ports, _testcmdline=None):
    """process_cmdline(_available_ports, _testcmdline="")

    _available_ports is a list? of port names
    _testcmdline can be list of strings that can be used to fake a command line.
    If None, the default
    command line processing is performed, otherwise,
    the list of strings in the argument is used.

    processes the command line arguments
    returns a tuple of (ui, verbose, cmdl_debug) if arguments are ok, Otherwise raises an exception
    """
    _tcl = []
    if _testcmdline:
        _tcl = _testcmdline
    tempargs = sys.argv[1:] + _tcl
    proc1(tempargs, _available_ports)
    #if not ('-h' in tempargs or '--help' in tempargs):
        #if _available_ports.isEmpty():
            #msg = 'no available communication port: aborting'
            #raise SystemExit(msg)
    #if '-h' in tempargs or '--help' in tempargs:
        #_PARSER.print_help()
        #raise SystemExit()

    if _testcmdline:
        args = _PARSER.parse_args(_testcmdline)
    else:
        args = _PARSER.parse_args()

    _aa = proc2(args, )
    possible_port = _aa[0]
    possible_ctrl = _aa[1]
    # if args.logdebug:
        # LOGGER.setLevel(logging.DEBUG)
    # elif args.loginfo:
        # LOGGER.setLevel(logging.INFO)

    #possible_port = args.Port
    # if args.Controller:
        #possible_ctrl = args.Controller
    # else:
        #possible_ctrl = 'dlxii'

    if len(_available_ports) != 1:
        if not args.Port.upper() in _available_ports:
            msg = 'Port {} not available: available ports are: {}, aborting' \
                .format(args.Port, _available_ports)
            raise Exception(msg)
    else:
        possible_port = _available_ports[0]

    ctrl = knowncontrollers.select_controller(possible_ctrl)
    if not ctrl:
        msg = 'Controller {} not available: available controlers are: {}, aborting' \
            .format(args.Controller, knowncontrollers.get_controller_ids())
        raise Exception(msg)

    verbose = args.verbose
    cmdl_debug = args.cldebug
    _ui = userinput.UserInput(ctrl[1])
    _ui.comm_port = possible_port
    if verbose:
        msg = '[verbose] ctrl:{}, port:{}, dbg:{}, verbose: True'\
            .format(ctrl, _ui.comm_port, cmdl_debug)
    return (_ui, verbose, cmdl_debug)


if __name__ == '__main__':
    pass
