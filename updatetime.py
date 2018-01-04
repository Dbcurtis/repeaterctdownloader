#!/usr/bin/env python3
"""This script updates the repeaters time"""
import sys
import time
import controller
import userinput
import getports

HOURLIM = 23
MINLIM = 50
O_DOW = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'foolsday']
R_DOW = [7, 6, 0, 1, 2, 3, 4, 5, ]
M_DOW = ['2', '3', '4', '5', '6', '7', '1', ]

TWO_CHAR = '{num:02d}'
def _delay():
    """_delay()

    if the time is >23:50, waits until 2 seconds after the date changes before continuing
    
    after the delay, returns the then current time.
    """
    while 1:
        os_time = time.localtime(time.time())
        if os_time.tm_hour < HOURLIM:
            break
        if os_time.tm_min < MINLIM:
            break
        delymin = os_time.tm_min - MINLIM
        time.sleep(delymin*60+2)
        return time.localtime(time.time())

def check_date(_res, _sdtpl, _os_time):
    """check_date(_res,_sdtpl,_os_time)

    _res is the dict set by gdtpl[2] that has keys A, m, d, Y
    with the same meaning as https://docs.python.org/3.0/library/time.html
    
    _sdtpl is the set date tuple
    
    _os_time is the current computer time
    """
    cmd = None
    dow = _res['A'].lower()
    m = _res['m']
    d = _res['d']
    Y = _res['Y']

    oY = str(_os_time.tm_year)
    om = TWO_CHAR.format(num=_os_time.tm_mon)
    od = TWO_CHAR.format(num=_os_time.tm_mday)
    owd = _os_time.tm_wday
    textdow = O_DOW[owd]
    aa = M_DOW[owd]
    if Y != oY or d != od or m != m or textdow != dow:
        arg = (_sdtpl[0], om, od, oY[2:4], aa, )
        cmd = _sdtpl[3](arg)
    return cmd

def check_time(_res, _sttpl, _os_time):
    """check_time(_res,_sttpl,_os_time)

    _res is the dict set by gttpl[2] that has keys I, M, p 
    with the same meaning as https://docs.python.org/3.0/library/time.html
    
    _sttpl is the set time tuple
    
    _os_time is the current computer time
    """
    cmd = None

    I = _res['I']
    M = _res['M']
    p = _res['p']
    pm = '0'
    if p[0:1] == 'P':
        pm = '1'

    cp = '0'
    if _os_time.tm_hour > 11:
        cp = '1'

    adjhour = _os_time.tm_hour
    if adjhour == 0 and cp == '0':
        adjhour = 12
    oH = TWO_CHAR.format(num=adjhour)
    oM = TWO_CHAR.format(num=_os_time.tm_min)
    if _os_time.tm_hour >= 13:

        oH = TWO_CHAR.format(num=_os_time.tm_hour-12)
        cp = '1'
    if I != oH or M != oM or pm != cp:
        arg = (_sttpl[0], oH, oM, cp)
        cmd = _sttpl[3](arg)

    return cmd

def main():
    """main()

    gets the port and repeater type from the command line arguments,
    reads the time and date from the controller
    reads the time from the opsys
    if it is close to a day change (within 10 min) Will delay until after the day change

    compares them and if more than 60 seconds difference updates the time on the controller
    """


    _available_ports = getports.GetPorts().get()
    print("Available serial ports are: %s" % _available_ports)

    _ui = userinput.UserInput()
    _ui.request()
    try:
        _ui.open()
        _c = controller.Controller(_ui)
        os_time = _delay()
        _c.open()
        ctrl = _c.ui.controller_type
        gdtpl = ctrl.newcmd_dict['gdate']
        gttpl = ctrl.newcmd_dict['gtime']
        sttpl = ctrl.newcmd_dict['stime']
        sdtpl = ctrl.newcmd_dict['sdate']
        cntdown = 15  #fifteen attempts max
        while cntdown > 0:
            cntdown -= 1
            try:
                if _c.sendcmd(gdtpl[0]):  #get date info from controller
                    _res = gdtpl[2](gdtpl[1].search(_c.last_response))
                    cmd = check_date(_res, sdtpl, time.localtime(time.time()))
                    if cmd:
                        if _c.sendcmd(cmd):
                            continue
                        else:
                            raise ValueError("retry date command send")
                    if _c.sendcmd(gttpl[0]):
                        _res = gttpl[2](gttpl[1].search(_c.last_response))
                        cmd = check_time(_res, gttpl, time.localtime(time.time()))
                        if cmd:
                            if _c.sendcmd(cmd):
                                break
                            else:
                                raise ValueError("retry time command send")
                        break
            except Exception as ve:  #do not really know what I am trying to catch here surly ValueError, but what others?
                time.sleep(10)  #10 sec sleep
                print(ve.args)
                      

        if cntdown > 0:
            pass
        _c.close()
        _ui.close()

    finally:
        _ui.close()


if __name__ == '__main__':

    try:
        main()
    except(Exception, KeyboardInterrupt) as exc:
        sys.exit(str(exc))
