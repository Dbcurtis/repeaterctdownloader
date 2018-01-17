#!/usr/bin/env python3
"""
Test file for updatetime
"""


import unittest
import time
import dlxii
import updatetime
import myserial
import userinput


class Testupdatetime(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass
    
    def testdelay(self):
        matchtime = time.strptime("03 Jan 2018 11 30 30", "%d %b %Y %H %M %S")
        result = updatetime._delay(debug=True, testtime=matchtime)
        curtime =  time.localtime(time.time())
        self.assertFalse(result[1])
        for a, b in zip(curtime, result[0]):
            self.assertEqual( a , b)

        matchtime = time.strptime("03 Jan 2018 23 56 30", "%d %b %Y %H %M %S")
        result = updatetime._delay(debug=True, testtime=matchtime)
        curtime =  time.localtime(time.time())
        self.assertTrue(result[1])
        self.assertTrue('4 min and 2' in result[1])

        matchtime = time.strptime("03 Jan 2018 23 59 30", "%d %b %Y %H %M %S")
        result = updatetime._delay(debug=True, testtime=matchtime)
        curtime =  time.localtime(time.time())
        self.assertTrue(result[1])
        self.assertTrue('1 min and 2' in result[1])

        matchtime = time.strptime("03 Jan 2018 23 59 59", "%d %b %Y %H %M %S")
        result = updatetime._delay(debug=True, testtime=matchtime)
        curtime =  time.localtime(time.time())
        self.assertTrue(result[1])
        self.assertTrue('1 min and 2' in result[1])

        matchtime = time.strptime("03 Jan 2018 23 50 59", "%d %b %Y %H %M %S")
        result = updatetime._delay(debug=True, testtime=matchtime)
        curtime =  time.localtime(time.time())
        self.assertTrue(result[1])
        self.assertTrue('10 min and 2' in result[1])

        matchtime = time.strptime("03 Jan 2018 23 50 00", "%d %b %Y %H %M %S")
        result = updatetime._delay(debug=True, testtime=matchtime)
        curtime =  time.localtime(time.time())
        self.assertTrue(result[1])
        self.assertTrue('10 min and 2' in result[1])

        matchtime = time.strptime("03 Jan 2018 23 49 59", "%d %b %Y %H %M %S")
        result = updatetime._delay(debug=True, testtime=matchtime)
        curtime =  time.localtime(time.time())
        self.assertFalse(result[1])
        
        matchtime = time.strptime("03 Jan 2018 23 00 00", "%d %b %Y %H %M %S")
        result = updatetime._delay(debug=True, testtime=matchtime)
        curtime =  time.localtime(time.time())
        self.assertFalse(result[1])
 
        
    def testcheckdate(self):

        cs = dlxii.Device()
        tup = cs.newcmd_dict['gdate']
        self.assertEqual('N029', tup[0])
        pat = tup[1]
        mdf = """total crap >"""
        mx = pat.search(mdf)
        self.assertFalse(mx)
         
        mdf = """DTMF>N029
This is Wednesday, 01-03-2018
OK
DTMF>"""        
        mx = pat.search(mdf)
        _res = tup[2](mx)
        sdtpl = cs.newcmd_dict['sdate']
        matchtime =  time.strptime("03 Jan 2018 11 30 30", "%d %b %Y %H %M %S")  
        cd = updatetime.check_date(_res, sdtpl, matchtime) #time.localtime(time.time()))
        self.assertFalse(cd)

        matchtime =  time.strptime("03 Jan 2017 11 30 30", "%d %b %Y %H %M %S")
        cd = updatetime.check_date(_res, sdtpl, matchtime)
        self.assertEqual('N0280103173', cd)

        matchtime =  time.strptime("01 Jan 2018 11 30 30", "%d %b %Y %H %M %S")  
        cd = updatetime.check_date(_res, sdtpl, matchtime) #time.localtime(time.time()))        
        self.assertEqual('N0280101182', cd)

        matchtime =  time.strptime("01 Feb 2018 11 30 30", "%d %b %Y %H %M %S")
        cd = updatetime.check_date(_res, sdtpl, matchtime) #time.localtime(time.time()))        
        self.assertEqual('N0280201185', cd)

        matchtime =  time.strptime("01 Jan 2018 11 30 30", "%d %b %Y %H %M %S")
        cd = updatetime.check_date(_res, sdtpl, matchtime) #time.localtime(time.time()))        
        self.assertEqual('N0280101182', cd)        

    def testchecktime(self):
        
        mdf = """DTMF>N027
The time is 12:23 P.M.
OK
DTMF"""
        cs = dlxii.Device()
        tup = cs.newcmd_dict['gtime']
        self.assertEqual('N027', tup[0])
        pat = tup[1]
        mx = pat.search(mdf)
        _res = tup[2](mx)
        sttpl = cs.newcmd_dict['stime']
        matchtime =  time.strptime("03 Jan 2018 12 23 30", "%d %b %Y %H %M %S")  
        cd = updatetime.check_time(_res, sttpl, matchtime) #time.localtime(time.time()))
        self.assertFalse(cd)

        matchtime =  time.strptime("03 Jan 2018 11 30 30", "%d %b %Y %H %M %S")
        cd = updatetime.check_time(_res, sttpl, matchtime)
        self.assertEqual('N02511300', cd)

        matchtime =  time.strptime("03 Jan 2018 00 30 30", "%d %b %Y %H %M %S")  
        cd = updatetime.check_time(_res, sttpl, matchtime) #time.localtime(time.time()))        
        self.assertEqual('N02512300', cd)

        matchtime =  time.strptime("03 Feb 2018 13 30 30", "%d %b %Y %H %M %S")
        cd = updatetime.check_time(_res, sttpl, matchtime) #time.localtime(time.time()))        
        self.assertEqual('N02501301', cd)

        matchtime =  time.strptime("03 Jan 2018 23 30 30", "%d %b %Y %H %M %S")
        cd = updatetime.check_time(_res, sttpl, matchtime) #time.localtime(time.time()))        
        self.assertEqual('N02511301', cd)        
    
        mdf = """DTMF>N027
The time is 12:23 A.M.
OK
DTMF"""    
        tup = cs.newcmd_dict['gtime']
        self.assertEqual('N027', tup[0])
        _res = tup[2](tup[1].search(mdf))
        sttpl = cs.newcmd_dict['stime']
        matchtime =  time.strptime("03 Jan 2018 00 23 30", "%d %b %Y %H %M %S")  
        cd = updatetime.check_time(_res, sttpl, matchtime) #time.localtime(time.time()))
        self.assertFalse(cd)

        matchtime =  time.strptime("03 Jan 2018 11 30 30", "%d %b %Y %H %M %S")
        cd = updatetime.check_time(_res, sttpl, matchtime)
        self.assertEqual('N02511300', cd)        
        
        matchtime =  time.strptime("03 Jan 2018 11 30 30", "%d %b %Y %H %M %S")
        cd = updatetime.check_time(_res, sttpl, matchtime)
        self.assertEqual('N02511300', cd)           
        
        mdf = """DTMF>N027
The time is 12:00 A.M.
OK
DTMF"""    
        tup = cs.newcmd_dict['gtime']
        self.assertEqual('N027', tup[0])
        _res = tup[2](tup[1].search(mdf))          
        sttpl = cs.newcmd_dict['stime']
        matchtime =  time.strptime("03 Jan 2018 00 00 00", "%d %b %Y %H %M %S")  
        cd = updatetime.check_time(_res, sttpl, matchtime) #time.localtime(time.time()))
        self.assertFalse(cd)

        matchtime =  time.strptime("03 Jan 2018 00 01 00", "%d %b %Y %H %M %S")  
        cd = updatetime.check_time(_res, sttpl, matchtime) #time.localtime(time.time()))
        self.assertEqual('N02512010', cd)

        matchtime =  time.strptime("03 Jan 2018 23 59 00", "%d %b %Y %H %M %S")  
        cd = updatetime.check_time(_res, sttpl, matchtime) #time.localtime(time.time()))
        self.assertEqual('N02511591', cd)         

        mdf = """DTMF>N027
The time is 12:00 P.M.
OK
DTMF"""    
        tup = cs.newcmd_dict['gtime']
        self.assertEqual('N027', tup[0])
        _res = tup[2](tup[1].search(mdf))
        sttpl = cs.newcmd_dict['stime']
        matchtime =  time.strptime("03 Jan 2018 12 00 00", "%d %b %Y %H %M %S")  
        cd = updatetime.check_time(_res, sttpl, matchtime) #time.localtime(time.time()))
        self.assertFalse(cd)

        matchtime =  time.strptime("03 Jan 2018 12 01 00", "%d %b %Y %H %M %S")  
        cd = updatetime.check_time(_res, sttpl, matchtime) #time.localtime(time.time()))
        self.assertEqual('N02512011', cd)

        matchtime =  time.strptime("03 Jan 2018 11 59 00", "%d %b %Y %H %M %S")  
        cd = updatetime.check_time(_res, sttpl, matchtime) #time.localtime(time.time()))
        self.assertEqual('N02511590', cd)    

        mdf = """DTMF>N027
The time is 12:01 P.M.
OK
DTMF"""    
        tup = cs.newcmd_dict['gtime']
        self.assertEqual('N027', tup[0])
        _res = tup[2](tup[1].search(mdf))
        sttpl = cs.newcmd_dict['stime']
        matchtime =  time.strptime("03 Jan 2018 12 01 00", "%d %b %Y %H %M %S")  
        cd = updatetime.check_time(_res, sttpl, matchtime) #time.localtime(time.time()))
        self.assertFalse(cd)

        matchtime =  time.strptime("03 Jan 2018 12 00 00", "%d %b %Y %H %M %S")  
        cd = updatetime.check_time(_res, sttpl, matchtime) #time.localtime(time.time()))
        self.assertEqual('N02512001', cd)

        matchtime =  time.strptime("03 Jan 2018 11 59 00", "%d %b %Y %H %M %S")  
        cd = updatetime.check_time(_res, sttpl, matchtime) #time.localtime(time.time()))
        self.assertEqual('N02511590', cd)        
    
        mdf = """DTMF>N027
The time is 11:59 A.M.
OK
DTMF"""    
        tup = cs.newcmd_dict['gtime']
        self.assertEqual('N027', tup[0])
        _res = tup[2](tup[1].search(mdf))  
        sttpl = cs.newcmd_dict['stime']
        matchtime =  time.strptime("03 Jan 2018 11 59 00", "%d %b %Y %H %M %S")  
        cd = updatetime.check_time(_res, sttpl, matchtime) #time.localtime(time.time()))
        self.assertFalse(cd)
        matchtime =  time.strptime("03 Jan 2018 12 00 00", "%d %b %Y %H %M %S")  
        cd = updatetime.check_time(_res, sttpl, matchtime) #time.localtime(time.time()))
        self.assertEqual('N02512001', cd)
        matchtime =  time.strptime("03 Jan 2018 11 58 00", "%d %b %Y %H %M %S")  
        cd = updatetime.check_time(_res, sttpl, matchtime) #time.localtime(time.time()))
        self.assertEqual('N02511580', cd)          
        
    def testdoit(self):
        msclass = myserial.MySerial
        msclass._debugging = True
        msclass._dbidx = 0  #test same date and time
        msclass._debugreturns = [
            b'preread ignored\r', b'\n9600 open default succeed DTMF>',
            b'DTMF>N029\r', b'\nThis is Wednesday, 01-03-2018\r', b'\nOK\r', b'\nDTMF>',
            b'DTMF>N027\r', b'\nThe time is 12:23 P.M.\r', b'\nOK\r', b'\nDTMF>',
                                 ]
        
        ui = userinput.UserInput(ctype=dlxii.Device())     
        ui.controller_type = dlxii.Device()
        ui.comm_port = 'COM3'
        ui.inputfn = 'updatetest.txt'
        matchtime =  time.strptime("03 Jan 2018 12 23 00", "%d %b %Y %H %M %S")  
        res = updatetime._doit(ui, debug_time=matchtime)
        self.assertTrue(res[2])
        self.assertEqual(14, res[0])
        self.assertTrue(14, res[1])
        
        msclass._dbidx = 0  # test same date differnt time
        msclass._debugreturns = [
            b'preread ignored\r', b'\n9600 open default succeed DTMF>',
            b'DTMF>N029\r', b'\nThis is Wednesday, 01-03-2018\r', b'\nOK\r', b'\nDTMF>',
            b'DTMF>N027\r', b'\nThe time is 12:23 P.M.\r', b'\nOK\r', b'\nDTMF>',
            b'DTMF>N02507071\r', b'\nTime set to 12:02 P.M.\r', b'\nOK\r', b'\nOK\r', b'\nDTMF>', 
            b'DTMF>N029\r', b'\nThis is Wednesday, 01-03-2018\r', b'\nOK\r', b'\nDTMF>',
            b'DTMF>N027\r', b'\nThe time is 12:02 P.M.\r', b'\nOK\r', b'\nDTMF>',
            b'\nDTMF>', b'\nDTMF>', b'\nDTMF>', b'\nDTMF>', b'\nDTMF>', b'\nDTMF>', b'\nDTMF>', 
                                 ]        
        matchtime =  time.strptime("03 Jan 2018 12 02 00", "%d %b %Y %H %M %S")  
        res = updatetime._doit(ui, debug_time=matchtime)
        self.assertTrue(res[1])
        self.assertEqual(13, res[0])
        self.assertFalse(res[2])
        
        msclass._dbidx = 0  # test differnt time and different date
        msclass._debugreturns = [
            b'preread ignored\r', b'\n9600 open default succeed DTMF>',
            b'DTMF>N029\r', b'\nThis is Tuesday, 01-02-2018\r', b'\nOK\r', b'\nDTMF>',
            b'DTMF>N0280103184\r', b'\nThis is Wednesday, 01-03-2018\r', b'\nOK\r', b'\nDTMF>',
            b'DTMF>N029\r', b'\nThis is Wednesday, 01-03-2018\r', b'\nOK\r', b'\nDTMF>',
            b'DTMF>N027\r', b'\nThe time is 12:23 P.M.\r', b'\nOK\r', b'\nDTMF>',
            b'DTMF>N02507071\r', b'\nTime set to 12:02 P.M.\r', b'\nOK\r', b'\nOK\r', b'\nDTMF>', 
            b'DTMF>N029\r', b'\nThis is Wednesday, 01-03-2018\r', b'\nOK\r', b'\nDTMF>',
            b'DTMF>N027\r', b'\nThe time is 12:02 P.M.\r', b'\nOK\r', b'\nDTMF>',
            b'\nDTMF>', b'\nDTMF>', b'\nDTMF>', b'\nDTMF>', b'\nDTMF>', b'\nDTMF>', b'\nDTMF>', 
                                 ]        
        matchtime =  time.strptime("03 Jan 2018 12 02 00", "%d %b %Y %H %M %S")  
        res = updatetime._doit(ui, debug_time=matchtime)
        self.assertTrue(res[1])
        self.assertEqual(12, res[0])
        self.assertFalse(res[2])          

    
if __name__ == '__main__':
    unittest.main()
