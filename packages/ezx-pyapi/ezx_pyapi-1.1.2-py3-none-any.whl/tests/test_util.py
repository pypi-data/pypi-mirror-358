'''
Created on 11 Mar 2022

@author: shalomshachne
'''
import unittest
from iserver import util
from iserver.msgs.OrderResponse import OrderResponse
from iserver.enums.msgenums import State
from iserver.msgs.Reject import Reject
from tests.data import test_data_factory

class Test(unittest.TestCase):

    def test_next_id(self):
        last_id = util.next_id()
        for x in range(1000):
            next_id = util.next_id()
            self.assertNotEqual(last_id, next_id, f'interation={x}')
            last_id = next_id


    def test_is_closed(self):
        response = OrderResponse(state=State.ACKED.value)
        self.assertFalse(util.is_closed(response), response.state)
        
        response.state = State.CAND.value
        self.assertTrue(util.is_closed(response), response.state)
        
        #test wrong kind of message
        reject = Reject()        
        self.assertFalse(util.is_closed(reject), 'no error on bad attribute')
        
    def test_format_order(self):
        order = test_data_factory.create_order_response()
        formatted = util.format_order(order)
        print(f'order={formatted}')
        
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_next_id']
    unittest.main()