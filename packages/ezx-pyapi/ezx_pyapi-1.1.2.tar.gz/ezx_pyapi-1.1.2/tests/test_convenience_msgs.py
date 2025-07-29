'''
Created on 21 Apr 2022

@author: shalomshachne
'''
import unittest

from iserver import util
from iserver.enums.api import IserverMsgSubType
from iserver.enums.msgenums import MsgType, Side, OrdType
from iserver.msgs.convenience_msgs import ReplaceOrder, CancelOrder, NewOrder
from tests.data import test_data_factory


class Test(unittest.TestCase):

    def testReplaceOrderStandardConstructor(self):
        orderId = test_data_factory.next_int_id()
        price = test_data_factory.random_price()
        qty = test_data_factory.random_quantity()
        
        replace = ReplaceOrder(orderId, price, qty)
        
        field = "api msg_subtype"
        self.assertEqual(IserverMsgSubType.ORDER.value, replace.msg_subtype, field)
                
        field = "msgType"
        self.assertEqual(MsgType.REPL.value, replace.msgType, field)
        
        field = "routerOrderID"
        self.assertEqual(orderId, replace.routerOrderID, field)
        
        field = "price"
        self.assertEqual(price, replace.price, field)
        
        field = "qty"
        self.assertEqual(qty, replace.orderQty, field)
    
    def testReplaceKwargsWorks(self):
        orderId = test_data_factory.next_int_id()
        account = util.next_id()
        args = {'account': account}
        replace = ReplaceOrder(orderId, **args)
        
        field = "api msg_subtype"
        self.assertEqual(IserverMsgSubType.ORDER.value, replace.msg_subtype, field)

        field = "routerOrderID"
        self.assertEqual(orderId, replace.routerOrderID, field)
        
        field = "account set from kwargs"
        self.assertEqual(account, replace.account, field)

    def testReplaceKwargsWorks2(self):
        orderId = test_data_factory.next_int_id()
        account = util.next_id()
        
        replace = ReplaceOrder(orderId, account=account)
        
        field = "api msg_subtype"
        self.assertEqual(IserverMsgSubType.ORDER.value, replace.msg_subtype, field)

        field = "routerOrderID"
        self.assertEqual(orderId, replace.routerOrderID, field)
        
        field = "account set from kwargs"
        self.assertEqual(account, replace.account, field)
    
    def testCancel(self):
        orderId = test_data_factory.next_int_id()
        cancel = CancelOrder(orderId)
        
        field = "api msg_subtype"
        self.assertEqual(IserverMsgSubType.ORDER.value, cancel.msg_subtype, field)
 
        field = "msgType"
        self.assertEqual(MsgType.CANC.value, cancel.msgType, field)
 
        field = "routerOrderID"
        self.assertEqual(orderId, cancel.routerOrderID, field)


    def testNewOrderWithBasicFields(self):
        #     order = OrderRequest(msgType=MsgType.NEW.value, symbol=symbol, side=parse_side(side), orderQty=qty, price=price, ordType=ordType, \
        # destination=destination, myID=util.next_id())
        
        symbol = test_data_factory.random_symbol()
        side = Side.SELL_PLUS.value
        price = test_data_factory.random_price()
        qty = test_data_factory.random_quantity()
        ordType = OrdType.LIMIT_ON_CLOSE.value
        destination = 'SIMU'
        id = util.next_id
                          
        order = NewOrder(symbol, side, qty, price, destination, id, ordType)
        
        field = "api msg_subtype"
        self.assertEqual(IserverMsgSubType.ORDER.value, order.msg_subtype, field)        
        
        field = "msgType"
        self.assertEqual(MsgType.NEW.value, order.msgType, field)       
        
        field = "symbol"
        self.assertEqual(symbol, order.symbol, field)       
        
        field = "side"
        self.assertEqual(side, order.side, field)       

        field = "qty"
        self.assertEqual(qty, order.orderQty, field)       

        field = "ordType"
        self.assertEqual(ordType, order.ordType, field)       

        field = "destination"
        self.assertEqual(destination, order.destination, field)       

        field = "myID"
        self.assertEqual(id, order.myID, field)       

        field = "symbol"
        self.assertEqual(symbol, order.symbol, field)       
        
        
    def testNewOrderWithKwargs(self):
        #     order = OrderRequest(msgType=MsgType.NEW.value, symbol=symbol, side=parse_side(side), orderQty=qty, price=price, ordType=ordType, \
        # destination=destination, myID=util.next_id())
        
        symbol = test_data_factory.random_symbol()
        side = Side.SELL_PLUS.value
        price = test_data_factory.random_price()
        qty = test_data_factory.random_quantity()
        ordType = OrdType.LIMIT_ON_CLOSE.value
        destination = 'SIMU'
        id = util.next_id
        
        account = 'acc' + str(test_data_factory.next_int_id())
                          
        order = NewOrder(symbol, side, qty, price, destination, id, ordType, account=account)
        
        field = "msgType"
        self.assertEqual(MsgType.NEW.value, order.msgType, field)               
        
        self.assertEqual(account, order.account, 'account set')
        
        
    def testNewOrderDefaultsOrdTypeToLimit(self):
        #     order = OrderRequest(msgType=MsgType.NEW.value, symbol=symbol, side=parse_side(side), orderQty=qty, price=price, ordType=ordType, \
        # destination=destination, myID=util.next_id())
        
        symbol = test_data_factory.random_symbol()
        side = Side.SELL_PLUS.value
        price = test_data_factory.random_price()
        qty = test_data_factory.random_quantity()
        destination = 'SIMU'
        id = util.next_id
        
        account = 'acc' + str(test_data_factory.next_int_id())
                          
        order = NewOrder(symbol, side, qty, price, destination, id, account=account)
        
        field = "msgType"
        self.assertEqual(MsgType.NEW.value, order.msgType, field)               
        
        field = 'account set'
        self.assertEqual(account, order.account, field)
                    
        field = 'defaulted ordType Limit'
        self.assertEqual(OrdType.LIMIT.value, order.ordType, field)
        
    def testNewOrderDefaultsOrdTypeToMarket(self):
        #     order = OrderRequest(msgType=MsgType.NEW.value, symbol=symbol, side=parse_side(side), orderQty=qty, price=price, ordType=ordType, \
        # destination=destination, myID=util.next_id())
        
        symbol = test_data_factory.random_symbol()
        side = Side.SELL_PLUS.value
        qty = test_data_factory.random_quantity()
                                  
        order = NewOrder(symbol, side, qty)
                            
        field = 'defaulted ordType Market'
        self.assertEqual(OrdType.MARKET.value, order.ordType, field)   
        
    def testNewOrderDefaultsOrdTypeToMarketPriceZero(self):
        #     order = OrderRequest(msgType=MsgType.NEW.value, symbol=symbol, side=parse_side(side), orderQty=qty, price=price, ordType=ordType, \
        # destination=destination, myID=util.next_id())
        
        symbol = test_data_factory.random_symbol()
        side = Side.SELL_PLUS.value
        qty = test_data_factory.random_quantity()
        
                         
        order = NewOrder(symbol, side, qty, None)
                            
        field = 'defaulted ordType Market'
        self.assertEqual(OrdType.MARKET.value, order.ordType, field)                
        self.assertIsNone(order.price, 'blanked out price')


    def testNewOrderWithNegativePrice(self):
            #     order = OrderRequest(msgType=MsgType.NEW.value, symbol=symbol, side=parse_side(side), orderQty=qty, price=price, ordType=ordType, \
            # destination=destination, myID=util.next_id())
            
            symbol = test_data_factory.random_symbol()
            side = Side.SELL_PLUS.value
            price = test_data_factory.random_price() * -1
            qty = test_data_factory.random_quantity()
            ordType = OrdType.LIMIT
            destination = 'SIMU'
            id = util.next_id
                              
            order = NewOrder(symbol, side, qty, price, destination, id, ordType)
            
            field = "price (with negative value)"
            self.assertEqual(price, order.price, field)       

    def testNewOrderWithNegativePriceNoOrdType(self):
            #     order = OrderRequest(msgType=MsgType.NEW.value, symbol=symbol, side=parse_side(side), orderQty=qty, price=price, ordType=ordType, \
            # destination=destination, myID=util.next_id())
            
            symbol = test_data_factory.random_symbol()
            side = Side.SELL_PLUS.value
            price = test_data_factory.random_price() * -1
            qty = test_data_factory.random_quantity()
            destination = 'SIMU'
            id = util.next_id
                              
            order = NewOrder(symbol, side, qty, price, destination, id, None)
            
            field = "price (with negative value)"
            self.assertEqual(price, order.price, field)
            
            field = "order type - autoset to LIMIT"
            self.assertEqual(OrdType.LIMIT.value, order.ordType)      

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testReplaceOrder']
    unittest.main()
