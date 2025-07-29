'''
Created on 11 Mar 2022

@author: shalomshachne
'''
import inspect
import random
import string

from iserver.enums.msgenums import LogonType, Side, Events, MsgType, ReturnCode
from iserver.net import ConnectionInfo
from iserver.msgs.OrderResponse import OrderResponse
from iserver.msgs.OrderRequest import OrderRequest
from iserver.msgs.OrderRequestInfo import OrderRequestInfo
from iserver.msgs.LogonResponse import LogonResponse


__next_int = 0

def create_connection_info(host='localhost', port=15000, user='aUser', password='aPasswd!', company='MyCompany', logon_type=LogonType.ALL.value):
    info = inspect.getargvalues(inspect.currentframe())
    args = dict(info.locals)
    args.pop('info')  # remove unexpected key/value 
    return ConnectionInfo(**args)
    
def next_int_id():
    global __next_int
    __next_int = __next_int + 1
    return __next_int

def random_symbol(max_chars : int =4) -> str:
    return ''.join(random.choices(string.ascii_uppercase, k=max_chars))

def random_price(min_price : float = .01, max_price : float = 999.99) -> float:
    return round(random.uniform(min_price, max_price), 2)

def random_quantity(min_qty : int = 1, max_qty : int = 5000):
    return random.randint(min_qty, max_qty)

def create_order_response(side = Side.BUY.value, symbol = random_symbol(), orderQty = random_quantity(), price=random_price()):
    return OrderResponse(side=side, symbol=symbol, orderQty=orderQty, price=price, routerOrderID=random_quantity(), event=Events.ORDR.value)

def create_new_order_request(side = Side.BUY.value, symbol = random_symbol(), orderQty = random_quantity(), price=random_price()):
    return OrderRequest(side=side, symbol=symbol, orderQty=orderQty, price=price, routerOrderID=random_quantity(), msgType = MsgType.NEW.value)
 
def create_new_order_request_info(side = Side.BUY.value, symbol = random_symbol(), orderQty = random_quantity(), price=random_price()):
    return OrderRequestInfo(side=side, symbol=symbol, orderQty=orderQty, price=price, routerOrderID=random_quantity(), msgType = MsgType.NEW.value)

def create_logon_response(returnCode : int = ReturnCode.OK.value, returnDesc : str = None):
    return LogonResponse(returnCode = returnCode, returnDesc = returnDesc)
  