'''
Created on 18 Apr 2022

@author: shalomshachne
'''
import unittest

from iserver.msgs import Reject
from tests.data import test_data_factory
from iserver import util, ezx_msg
from pip._internal import req


class Test(unittest.TestCase):


    def setUp(self):
        self.reject = Reject.Reject()


    def tearDown(self):
        pass


    def testDecodeRejectWithOrderRequest(self):
        req = test_data_factory.create_new_order_request_info()
        req.myID = util.next_id()
        
        reject = self.reject
        reject.msgType = req.msgType
        reject.myID = req.myID
        reject.rejectedRequest = req
        reject.returnCode = Reject.REJECT_BUYING_POWER_EXCEEDED
        reject.returnDesc = "REJECT_BUYING_POWER_EXCEEDED"
        
        encoded = ezx_msg.encode(reject)
        decoded = ezx_msg.decode_message(reject.msg_subtype, encoded)
        
        self.assertEqual(reject.returnCode, decoded.returnCode, "returnCode")
        self.assertEqual(Reject.REJECT_BUYING_POWER_EXCEEDED, decoded.returnCode)
        self.assertEqual(reject.returnDesc, decoded.returnDesc)
        
        self.assertEqual(req, decoded.rejectedRequest, 'decoded the rejected request')
        
        
        
        
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()