'''
Created on Oct 6, 2021

@author: Sgoldberg
'''
import unittest

import iserver
from iserver.msgs import LogonRequest


class Test(unittest.TestCase):


    def test_to_bean_string(self):
        l = LogonRequest()
        l.msg_type = None
        l.msg_subtype = None
        l.seqNo = None
        l.userName = 'gnadan'
        l.password = 'mypass'
        expected = 'password=mypass, userName=gnadan'
        actual = iserver.to_bean_string(l)
        self.assertEqual(expected, actual)
        
        actual = str(l)
        self.assertEqual(expected, actual, "inherited to_string method")

    def test_to_bean_string_all(self):
        l = LogonRequest()
        l.userName = 'gnadan'
        l.password = 'mypass'
        expected = 'password=mypass'
        actual = iserver.to_bean_string(l, lambda x : True)
        self.assertTrue(expected in actual)
        expected = 'companyName=None'
        self.assertTrue(expected in actual)
        
        print("str(logon)=" + actual)
        
        expected = actual
        r = repr(l)
        self.assertEqual(expected, r, 'rpr function returns all properties')
        
        
        
        
#         actual = str(l)
#         self.assertEqual(expected, actual, "inherited to_string method")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()