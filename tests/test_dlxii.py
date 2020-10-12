#!/usr/bin/env python3
"""
Test file for dlxii
"""
from __future__ import print_function
import unittest
import dlxii


class TestControllerspecific(unittest.TestCase):
    """test"""

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

    def testcreation(self):
        """tbd"""
        cs = dlxii.Device()
        self.assertEqual('RLC-Club Deluxe II v2.15', cs.get_Ctr_type)
        cpsData = cs.cps_data
        cps0 = cpsData[0]
        self.assertEqual('[CPS: 960, 0.215]', str(cps0))
        self.assertEqual(9600, cps0.bps)
        self.assertTrue(0.21 < cps0.cpsDelay < 0.22)
        ss = '[CPS: 960, 0.215]'
        self.assertEqual(ss, str(cps0))
        rates = [d.bps for d in cs.cps_data]
        self.assertEqual([9600, 19200, 4800, 2400, 1200, 600, 300], rates)
        css = 'RLC-Club Deluxe II v2.15'
        self.assertEqual(css, str(cs))

    def testnewcmd_dict(self):
        cs = dlxii.Device()
        mdf = """DTMF>N054 501N054501
Macro 501 contains 2 commands:
  #00  Command #038 with 00 digits of data:
  #01  Command #000 with 02 digits of data: 13
This macro is 9 percent full
OK
OK
DTMF>"""
        tup = cs.newcmd_dict['rmc']
        self.assertEqual('N054', tup[0])
        pat = tup[1]
        mx = pat.search(mdf)
        res = mx.groupdict()
        self.assertEqual('2', res['numins'])
        self.assertEqual('9', res['full'])
        self.assertEqual('501', res['macro'])
        cmdraw = res['cmds'].strip()
        cmdlines = [l for l in cmdraw.split('\n') if l.strip()]
        self.assertEqual(2, len(cmdlines))
        self.assertTrue('#038' in cmdlines[0])
        self.assertTrue('#000' in cmdlines[1])

        mx = pat.search(mdf)
        res = tup[2](mx)
        self.assertEqual('2', res['numins'])
        self.assertEqual('9', res['full'])
        self.assertEqual('501', res['macro'])
        self.assertEqual(2, len(res['cmds']))
        cmdlines = res['cmds']
        self.assertTrue('#038' in cmdlines[0])
        self.assertTrue('#000' in cmdlines[1])

        mdf = """OK
DTMF>N011 521N011521
Command number 521 is named C47571.  It takes 0 digits of data.
OK
OK
DTMF>"""
        tup = cs.newcmd_dict['rcn']
        self.assertEqual('N011', tup[0])
        pat = tup[1]
        mx = pat.search(mdf)
        res = tup[2](mx)
        self.assertEqual('521', res['cmdno'])
        self.assertEqual('C47571', res['name'])
        self.assertEqual('0', res['digs'])

        mdf = """DTMF>N029
This is Wednesday, 01-03-2018
OK
DTMF>"""
        tup = cs.newcmd_dict['gdate']
        self.assertEqual('N029', tup[0])
        pat = tup[1]
        mx = pat.search(mdf)
        res = tup[2](mx)
        self.assertEqual('Wednesday', res['A'])
        self.assertEqual('01', res['m'])
        self.assertEqual('03', res['d'])
        self.assertEqual('2018', res['Y'])

        mdf = """DTMF>N027
The time is 12:23 P.M.
OK
DTMF"""
        tup = cs.newcmd_dict['gtime']
        self.assertEqual('N027', tup[0])
        pat = tup[1]
        mx = pat.search(mdf)
        res = tup[2](mx)
        self.assertEqual('12', res['I'])
        self.assertEqual('23', res['M'])
        self.assertEqual('P.M.', res['p'])

    def testfmtcmd(self):
        cs = dlxii.Device()
        tup = cs.newcmd_dict['sdate']
        arg = (tup[0], 'arg1', 'arg2', 'arg3', 'arg4')
        cmd = tup[3](arg)
        self.assertEqual('N028arg1arg2arg3arg4', cmd)

    def testfmt_rmc(self):
        cs = dlxii.Device()
        r = cs.fmtRMC("junk test")
        self.assertEqual("junk test", r[0])
        self.assertEqual({}, r[1])
        mdf = """DTMF>N054 501N054501
Macro 501 contains 2 commands:
  #00  Command #038 with 00 digits of data:
  #01  Command #000 with 02 digits of data: 13
This macro is 9 percent full
OK
OK
DTMF>"""
        r = cs.fmtRMC(mdf)
        self.assertEqual('Macro 501 contains 2 commands\n'
                         '#00  Command #038 with 00 digits of data:\n'
                         '#01  Command #000 with 02 digits of data: 13\n'
                         'This macro is 9 percent full',
                         r[0])
        self.assertEqual(4, len(r[1]))
        self.assertEqual(2, len(r[1].get("cmds")))

    def testfmt_rcm(self):
        cs = dlxii.Device()
        r = cs.fmtRMC("junk test")
        self.assertEqual("junk test", r[0])
        self.assertEqual({}, r[1])
        mdf = """OK
DTMF>N011 521N011521
Command number 521 is named C47571.  It takes 0 digits of data.
OK
OK
DTMF>"""
        _ = cs.fmtRCM(mdf)
        self.assertEqual('Command number 521 is named C47571.  It takes 0 digits of data.',
                         _[0])
        self.assertEqual(3, len(_[1]))


if __name__ == '__main__':
    unittest.main()
