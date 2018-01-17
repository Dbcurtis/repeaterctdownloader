#!/usr/bin/env python3
"""This script updates the repeaters time"""
import sys
import argparse
import time

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

_PARSER = argparse.ArgumentParser(description="Sets a controller's date and time if needed",
                                  epilog="Useful for running in a cron job"
                                 )
_PARSER.add_argument('Controller', nargs='?', default='dlx2',
                     help='Controller type, one of [dlx2, rlc1+] dlx2 is default'
                    )
_PARSER.add_argument('Port',
                     help='Port id if required, if only one open port, that one will be used'
                    )
def _NOOP(a):
    pass

CLOSER = {False: lambda a: a.close(), True: lambda a: _NOOP(a)}

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
    return cmd

def check_time(_res, _sttpl, _os_time):
    """check_time(_res,_sttpl,_os_time)

    _res is the dict set by gttpl[2] that has keys I, M, p
    with the same meaning as https://docs.python.org/3.0/library/time.html

    _sttpl is the set time tuple

    _os_time is the current computer time

    return None if the repeater time and the computer time match
    otherwise returns the command to set the repeater time.
    """
    cmd = None

    _I = _res['I']
    _M = _res['M']
    _p = _res['p']
    _pm = '0'
    if _p[0:1] == 'P':
        _pm = '1'

    _cp = '0'
    if _os_time.tm_hour > 11:
        _cp = '1'

    _adjhour = _os_time.tm_hour
    if _adjhour == 0 and _cp == '0':
        _adjhour = 12
    oH = TWO_CHAR.format(num=_adjhour)
    oM = TWO_CHAR.format(num=_os_time.tm_min)
    if _os_time.tm_hour >= 13:
        oH = TWO_CHAR.format(num=_os_time.tm_hour-12)
        _cp = '1'
    if not (_I == oH and _M == oM and _pm == _cp):
        arg = (_sttpl[0], oH, oM, _cp)
        cmd = _sttpl[3](arg)

    return cmd

def process_cmdline():
    """process_cmdline()

    processes the command line arguments
    returns a UserInput if arguments are ok, Otherwise raises an exception
    """
    _available_ports = getports.GetPorts().get()
    args = _PARSER.parse_args()
    if not args.Port.upper() in _available_ports:
        msg = 'Port {} not available: available ports are: {}, aborting' \
            .format(args.Port, _available_ports)
        raise Exception(msg)

    ctrl = knowncontrollers.select_controller(args.Controller)
    if not ctrl:
        msg = 'Controller {} not available: available controlers are: {}, aborting' \
            .format(args.Controller, knowncontrollers.get_controller_ids())
        raise Exception(msg)

    _ui = userinput.UserInput()
    _ui.controller_type = ctrl
    _ui.serial_port = args.Port
    return _ui

def _doit(_ui, debug_time=None):
    """doit(_ui)

    does all the work
    _ui is the UserInput

    returns    cntdown, succ, noneed which is the countdown, if successful, if not needed

    """
    result = ()
    _the_time = {False:  debug_time, True:time.localtime(time.time()),}
    try:

        def setdate():
            """setdate()

            checks to see if the dates are different, and if so, generates and executes a command
            to the controller

            returns with the command if a command was needed, or None if no date change was required
            """
            cmd = None
            if _c.sendcmd(gdtpl[INST]):  #get date info from controller
                _res = gdtpl[REPL_FMT](gdtpl[PAT].search(_c.last_response))
                systime = _the_time.get(debug_time is None)
                cmd = check_date(_res, sdtpl, systime)
                if cmd and not _c.sendcmd(cmd):
                    raise ValueError("retry date command send error")
            return cmd

        def settime():
            """settime()

            checks to see if the times are different, and if so, generates and executes a command
            to the controller

            returns with the command if a command was needed, or None if no time change was required
            """
            cmd = None
            if _c.sendcmd(gttpl[INST]):
                _res = gttpl[REPL_FMT](gttpl[PAT].search(_c.last_response))
                systime = _the_time.get(debug_time is None)
                cmd = check_time(_res, sttpl, systime)
                if cmd and not _c.sendcmd(cmd):
                    raise ValueError("retry time command send error")
            return cmd

        _ui.open()
        _c = controller.Controller(_ui)
        _c.open()
        ctrl = _c.ui.controller_type
        gdtpl = ctrl.newcmd_dict['gdate']
        gttpl = ctrl.newcmd_dict['gtime']
        sttpl = ctrl.newcmd_dict['stime']
        sdtpl = ctrl.newcmd_dict['sdate']
        cntdown = SET_ATTEMPT_MAX  #fifteen attempts max
        while cntdown > 0:
            cntdown -= 1
            try:

                #check the dates are the same and if not make them so
                if setdate():
                    continue  #made a change, try again

                if not settime():
                    break
                   # continue  #made a change try again

            except Exception as _ve:  #do not really know what I am trying to catch here
                # shurly ValueError, but what others?
                time.sleep(10)  #10 sec sleep
                print(_ve.args)

        succ = cntdown > 0
        noneed = cntdown == SET_ATTEMPT_MAX - 1
        result = (cntdown, succ, noneed)
        ifa = {True: 'Controller date-time was current',
               False:"Controller time sucessfully set: {}" .format(succ),}
        print(ifa.get(noneed))

        _c.close()
        _ui.close()

    finally:

        CLOSER.get(_c is None)(_c)
        CLOSER.get(_ui is None)(_ui)
        #if _c:
            #_c.close()
        #if _ui:
            #_ui.close()

    return result

def main():
    """main()

    gets the port and repeater type from the command line arguments,
    reads the time and date from the controller
    reads the time from the opsys
    if it is close to a day change (within 10 min) Will delay until after the day change

    compares them and if more than 60 seconds difference updates the time on the controller
    """
    _ui = None
    _c = None

    _ui = process_cmdline()
    _delay()
    _doit(_ui)

if __name__ == '__main__':

    try:
        main()
    except(Exception, KeyboardInterrupt) as exc:
        sys.exit(str(exc))
