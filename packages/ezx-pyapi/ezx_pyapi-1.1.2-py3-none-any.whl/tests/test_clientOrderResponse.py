'''
Created on 11 Feb 2022

@author: shalomshachne
'''
import unittest
from iserver.msgs.ExecutionStatus import ExecutionStatus
from iserver.msgs.ClientOrderResponse import ClientOrderResponse


class Test(unittest.TestCase):


    def setUp(self):
        self.response = ClientOrderResponse()


    def tearDown(self):
        pass


    def testKwArgsConstructor(self):
        e = ExecutionStatus()
        self.response.execStatus = e
        self.response.symbol = "XYZ"
        
        response2 = ClientOrderResponse(execStatus = e, symbol = self.response.symbol)
        self.assertEqual(self.response, response2)
        self.assertEqual(e, response2.execStatus, "set the ExecStatus property")
        
        
