#!/usr/bin/env python3
"""This script updates the repeater's time and date"""
import sys
import os
import argparse
import time
import datetime
import logging
import logging.handlers
import knowncontrollers
import controller
import userinput
import getports
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
    if not (_Y == _oY and _d == _od and _m == _m and textdow == dow):
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
    if not ('-h' in tempargs or '--help' in tempargs):
        if len(_available_ports) < 1:
            msg = 'no available communication port: aborting'
            raise SystemExit(msg)
    if '-h' in tempargs or '--help' in tempargs:
        _PARSER.print_help()
        raise SystemExit()

    if _testcmdline:
        args = _PARSER.parse_args(_testcmdline)
    else:
        args = _PARSER.parse_args()

    if args.logdebug:
        LOGGER.setLevel(logging.DEBUG)
    elif args.loginfo:
        LOGGER.setLevel(logging.INFO)

    possible_port = args.Port
    if args.Controller:
        possible_ctrl = args.Controller
    else:
        possible_ctrl = 'dlxii'

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


class Stuff:
    """Stuff

    """
    def __init__(self, uiintuple):
        self._ui = uiintuple[0]
        self.verbose = uiintuple[1]
        self.cmdl_debug = uiintuple[2]
        self._ct = None
        _delay()

    def _helper1(self, cmd, msg):

        if not self.cmdl_debug:
            if cmd and not self._ct.sendcmd(cmd, display=self.verbose or self.cmdl_debug):
                raise ValueError("retry {} command send error".format(msg))
        else:
            print("debugging, would have set {} with {}".format(msg, cmd))

    def doit(self, debug_time=None):
        """doit(_debug_time=)

        does all the work
        _ui is the UserInput

        returns    (cntdown, succ, noneed) which is the countdown, if successful, if not needed

        """

        verbose = self.verbose
        cmdl_debug = self.cmdl_debug
        result = ()
        _the_time = {False:  debug_time, True:time.localtime(time.time()),}
        try:

            def setdate():
                """setdate()

                checks to see if the dates are different, and if so,
                generates and executes a command
                to the controller

                returns with the command if a command was needed,
                or None if no date change was required

                if command error, raises ValueError("retry date command send error")
                """

                gdtpl = ctrl.newcmd_dict['gdate']
                sdtpl = ctrl.newcmd_dict['sdate']
                cmd = None
                _the_time[True] = time.localtime(time.time())
                if self._ct.sendcmd(gdtpl[INST], cmdl_debug or verbose):
                    #get date info from controller
                    _res = gdtpl[REPL_FMT](gdtpl[PAT].search(_c.atts['last_response']))
                    if verbose:
                        print(_c.atts['last_response'])
                    systime = _the_time.get(debug_time is None)
                    cmd = check_date(_res, sdtpl, systime)
                    self._helper1(cmd, 'date')
                    if verbose:
                        print(time.localtime(time.time()))

                return cmd

            def settime():
                """settime()

                checks to see if the times are different,
                and if so, generates and executes a command
                to the controller

                returns with the command if a command was needed,
                or None if no time change was required
                if command error raises ValueError("retry date command send error")
                """
                cmd = None
                gttpl = ctrl.newcmd_dict['gtime']
                sttpl = ctrl.newcmd_dict['stime']
                _the_time[True] = time.localtime(time.time())
                if _c.sendcmd(gttpl[INST], cmdl_debug or verbose):
                    _res = gttpl[REPL_FMT](gttpl[PAT].search(_c.atts['last_response']))
                    systime = _the_time.get(debug_time is None)
                    if verbose:
                        print(_c.atts['last_response'])
                    cmd = check_time(_res, sttpl, systime)
                    self._helper1(cmd, 'time')
                return cmd

            _ui = self._ui
            _ui.open()
            self._ct = controller.Controller(_ui)
            _c = self._ct
            _c.open()

            ctrl = _c.ui.controller_type
            cntdown = SET_ATTEMPT_MAX  #fifteen attempts max
            while cntdown > 0:
                cntdown -= 1
                try:

                    #check the dates are the same and if not make them so
                    if setdate():
                        LOGGER.info("date changed")
                        if verbose:
                            print('date change, try again')
                        continue  #made a change, try again

                    if not settime():
                        break
                    #continue  #made a change try again
                    LOGGER.info("time changed")
                    if verbose:
                        print('time change, try again')


                except Exception as _ve:  #do not really know what I am trying to catch here
                    # shurly ValueError, but what others?
                    LOGGER.debug("10 second sleep")
                    time.sleep(10)  #10 sec sleep
                    print(_ve.args)

            succ = cntdown > 0
            if verbose:
                print('cntdown: {}'.format(cntdown))
            noneed = cntdown == SET_ATTEMPT_MAX - 1
            result = (cntdown, succ, noneed)
            if self.verbose:
                ifa = {True: 'Controller date-time was current',}
                ifa[False] = "Controller time sucessfully set: {}" .format(succ)
                #_jjj = []
                #_jjj.append(str(datetime.datetime.now()))
                #_jjj.append(ifa.get(noneed))
                print(' '.join([str(datetime.datetime.now()), ifa.get(noneed), ]))

            _c.close()
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
    THE_LOGGER.info('updatetime executed as main')
    #LOGGER.setLevel(logging.DEBUG)

    try:
        main()
    except SystemExit as sex:
        print(sex)
    except(Exception, KeyboardInterrupt) as exc:
        print(str(exc))
        sys.exit(str(exc))
