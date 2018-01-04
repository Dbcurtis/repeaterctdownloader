#!/usr/bin/env python3
"""
Test file for updatetime
"""

import sys
import unittest
import time
import dlxii
import updatetime


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
    
    def testcheckdate(self):
        
        mdf = """DTMF>N029
This is Wednesday, 01-03-2018
OK
DTMF>"""
        cs = dlxii.DlxII()
        tup = cs.newcmd_dict['gdate']
        self.assertEqual('N029', tup[0])
        pat = tup[1]
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
        cs = dlxii.DlxII()
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
        
if __name__ == '__main__':
    unittest.main()
