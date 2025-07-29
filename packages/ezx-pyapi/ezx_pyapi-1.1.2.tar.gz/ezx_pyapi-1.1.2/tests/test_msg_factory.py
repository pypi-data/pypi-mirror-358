'''
Created on Oct 25, 2021

@author: Sgoldberg
'''
import unittest
from iserver import msg_factory
from iserver.msgs import ExecutionStatus
from iserver.msgs.OrderRequest import OrderRequest
from iserver.msgs.StrategyInfo import StrategyInfo


class Test(unittest.TestCase):


    def test_get_block_message(self):
        block = 'EB'
        m = msg_factory.get_block_message(block, None)
        self.assertIsInstance(m, ExecutionStatus)
        
        block = 'unknown'
        self.assertIsNone(msg_factory.get_block_message(block, None))
        
    
    def test_get_block_message_for_name_collision(self):
        block_tag = 'STGBLK'
        req = OrderRequest()
        msg = msg_factory.get_block_message(block_tag, req)
        self.assertIsInstance(msg, StrategyInfo)
        
        



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_get_block_message']
    unittest.main()