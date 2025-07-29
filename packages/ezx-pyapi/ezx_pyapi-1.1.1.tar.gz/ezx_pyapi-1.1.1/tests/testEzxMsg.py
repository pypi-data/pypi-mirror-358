'''
Created on Oct 29, 2021

@author: Sgoldberg
'''
import unittest

from iserver.EzxMsg import EzxMsg
from iserver.msgs import OrderResponse, Field, noop_decode_func, \
    update_list_item
from iserver.msgs.OrderRequest import OrderRequest


class MsgChild(EzxMsg):
    __block_fields__ = {
        'ORB' : Field('legList', 'ORB', noop_decode_func, update_list_item), 
        'ALLOCABLK' : Field('allocsList', 'ALLOCABLK', noop_decode_func, update_list_item), 
    }
    
class MsgGrandChild(MsgChild):
        __block_fields__ = {
        'STGBLK' : Field('legList', 'STGBLK', noop_decode_func, update_list_item)
    }

class MsgGreatGrandChild(MsgGrandChild):
        __block_fields__ = {
        'HOBO' : Field('legList', 'HOBO', noop_decode_func, update_list_item)
    }

class Test(unittest.TestCase):


    def testGetBlockFieldByNameFindsField(self):
        orderResponse = OrderResponse()
        f = orderResponse.get_block_field_by_name('executions')
        self.assertIsNotNone(f)
        self.assertEqual('executions', f.name)
        
    def testGetBlockFieldByNameFindsFieldWhenParent(self):
        order = OrderRequest();
        f = order.get_block_field_by_name('strategyInfo')
        self.assertIsNotNone(f)
        self.assertEqual('strategyInfo', f.name)

    
    def testGetBlockFieldChecksClassHeirarchy(self):
        # test that get_block_field navigates the message heirarchy.
        msg = MsgGreatGrandChild()
        toCheck = [ MsgGreatGrandChild, MsgGrandChild, MsgChild ]        
        for c in toCheck:
            obj = c()
            d = obj.__block_fields__
            for name in d:
                f = msg.get_block_field(name)
                self.assertIsNotNone(f, f'found field for {name}, originating from class={c}')
                
    def testGetBlockFieldOwner(self):
        msg = MsgGreatGrandChild()
        toCheck = [ MsgGreatGrandChild, MsgGrandChild, MsgChild ]        
        for c in toCheck:
            obj = c()
            d = obj.__block_fields__
            for name in d:
                found = msg.get_block_field_owner(name)
                self.assertEqual(c, found, f'got correct owner class for {name}')
                
    def testGetBlockFieldMethodsReturnNoneIfNotFound(self):
        msg = MsgGreatGrandChild()
        name = 'notexist'
        self.assertIsNone(msg.get_block_field_owner(name))
        self.assertIsNone(msg.get_block_field(name))
        self.assertIsNone(msg.get_block_field_by_name(name))
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testGetBlockFieldByName']
    unittest.main()