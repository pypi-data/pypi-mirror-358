'''
Created on Sep 29, 2021

@author: Sgoldberg
'''

import unittest

from iserver.msgs import LogonRequest


SAMPLE_MSG = "00010402100000\001CONAM=FEIS\001DTGMT=<TODAY>\001TYPE=3\001PWD=igor\001SEQ=0\001UNAM=igor\001SNDDESTSTRAT=1\001SNDSETS=1\001DSTAT=1\001OMSVER=4.0.1\001\003"

class Test(unittest.TestCase):

    def setUp(self):
        self.logon = LogonRequest()


    def tearDown(self):
        pass


    def testConstructorWithSeqNo(self):
        seqno = 101
        l = LogonRequest(seqNo = seqno)
        self.assertEqual(seqno, l.seqNo)


    def testEncode(self):
        expected = SAMPLE_MSG
        c = expected[14]
        self.assertEqual(1, ord(c), "ASCII 1 correct")
        c = expected[-1]
        self.assertEqual(3, ord(c), "ASCII 3 correct")
        
        logon = self.logon
        logon.companyName = 'FEIS'                
        logon.user = 'igor'
        logon.password = 'igor'
        logon.date = '<TODAY>'
        logon.logonType = 3
        logon.sendDestStrategies = 1
        logon.sendSettings = 1
        logon.sendDestinationState = 1
        logon.omsVersion = "4.0.1"
        
        msg_only = expected[15:-1]
        print('msg=' + msg_only)
        
    def testMsgTypeAndSubType(self):
        logon = self.logon
        self.assertEqual(2, logon.msg_type, "correct msgtype")
        self.assertEqual(100, logon.msg_subtype, "correct msgtype")
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()