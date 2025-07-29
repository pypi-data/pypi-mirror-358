'''
Created on 23 Feb 2022

@author: shalomshachne
'''
import unittest
from iserver.msgs.YieldData import YieldData
import iserver.enums
from iserver import ezx_msg


class Test(unittest.TestCase):

    def setUp(self):
        self.y = YieldData()

    def testYield(self):
        self.y.myYield = .023512
        self.y.yieldType = 'FIXED'
        
        encoded = ezx_msg.encode(self.y)
        y2 = YieldData()
        ezx_msg.populate_message(y2, encoded)
        self.assertEqual(self.y, y2)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testYield']
    unittest.main()
