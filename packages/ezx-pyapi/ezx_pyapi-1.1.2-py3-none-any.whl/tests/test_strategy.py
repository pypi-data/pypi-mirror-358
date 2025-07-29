'''
Created on 18 Feb 2022

@author: shalomshachne
'''
import unittest
import iserver
from iserver.msgs.StrategyInfo import StrategyInfo
from iserver.msgs.TagValueMsg import TagValueMsg
from iserver import ezx_msg
from iserver.enums.api import IserverMsgSubType
from iserver.msgs.OrderRequest import OrderRequest
from pip._internal import req


class Test(unittest.TestCase):


    def setUp(self):
        self.strategy_info = StrategyInfo()
        self.order_request = OrderRequest()
        


    def tearDown(self):
        pass


    def testDecode(self):
        encoded = 'SYM=symbol-2B=STGBLKSTGYNM=1645193523396-1STRATINFOID=1B=STRATTVSkey1=1645193523396-2key2=1645193523396-3E=STRATTVSE=STGBLK'
        
        req = ezx_msg.decode_message(IserverMsgSubType.ORDER.value, encoded)
        self.assertIsNotNone(req, "decoded request")
        
        expected = 'symbol-2'
        actual = req.symbol 
        self.assertEqual(expected, actual, "symbol")
        
        info = req.strategyInfo
        self.assertIsNotNone(info, "created strategy info")
        
        msg = 'strategyName'
        expected = '1645193523396-1'
        actual = info.strategyName
        self.assertEqual(expected, actual, msg)
        
        msg = 'strategyInfoID'
        expected = 1
        actual = info.strategyInfoID
        self.assertEqual(expected, actual, msg)
        
        
        msg = 'tagValueMsg'
        tv_msg = info.strategyTVS
        self.assertIsInstance(tv_msg, TagValueMsg, msg)
        
        index1 = encoded.index('key1')
        index2 = encoded.index('E=STRATTVS')
        values = encoded[index1:index2]
        d = iserver.parse_to_dict(values)
        msg = 'dictionaries match'
        self.assertDictEqual(d, tv_msg.tag_values, msg)
        
         
    def testEncodeStrategyBlock(self):
        encoded = 'SYM=symbol-2B=STGBLKSTGYNM=1645193523396-1STRATINFOID=1B=STRATTVSkey1=1645193523396-2key2=1645193523396-3E=STRATTVSE=STGBLK'        
        req = ezx_msg.decode_message(IserverMsgSubType.ORDER.value, encoded)           
        encoded2 = ezx_msg.encode(req)
        print(f'encoded2={encoded2}')
        self.assertEqual(encoded, encoded2, 'encoded matches API message')
        
        req2 = ezx_msg.decode_message(IserverMsgSubType.ORDER.value, encoded2)    
        self.assertEqual(req, req2, 'order requests match')
        
        
        
    def testGetSuperClassFields(self):
        req = OrderRequest()
        
        fields = req.__block_fields__
        self.assertTrue('ORB' in fields)
        self.assertTrue(fields.__contains__('ORB'))
        
    
    def testGetBlockFieldFromSuperClass(self):
        req = OrderRequest()
        name = 'ORB'
        f = req.get_block_field(name)
        self.assertIsNotNone(f, f'got field for {name}')
        
        name = 'STGBLK'
        f = req.get_block_field(name)
        self.assertIsNotNone(f, f'got field for {name}')
        
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()