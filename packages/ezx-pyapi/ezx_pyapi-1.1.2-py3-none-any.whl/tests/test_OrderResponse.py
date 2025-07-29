'''
Created on Nov 9, 2021

@author: samgo_000
'''
import unittest
from iserver.enums.msgenums import State

from iserver.msgs import OrderResponse


class Test(unittest.TestCase):

    def testConstructorWithKeyWordArgs(self):
        sym = 'ABC'
        side = 2
        order_qty = 100
        price = 10
        or1 = OrderResponse()
        or1.symbol = sym
        or1.side = side
        or1.orderQty = order_qty
        or1.price = price
        
        or2 = OrderResponse(symbol=sym, side=side, orderQty=order_qty, price=price)
        self.assertEqual(or1, or2)
    
    def testEnumTypeInStateField(self):
        sym = 'ABC'
        side = 2
        order_qty = 100
        price = 10
        or1 = OrderResponse()
        or1.symbol = sym
        or1.side = side
        or1.orderQty = order_qty
        or1.price = price
        or1.state = 'ACKED'
        
        self.assertEqual(State.ACKED.value, or1.state, "state enum matches string value")
        
        

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testConstructorWithKeyWordArgs']
    unittest.main()
