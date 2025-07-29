'''
Created on 16 Mar 2022
Subclasses of API messages tuned to specific use cases
@author: shalomshachne
'''
from iserver.msgs.OrderRequest import OrderRequest
from iserver.enums.msgenums import MsgType, OrdType


class NewOrder(OrderRequest):
    
    def __init__(self, symbol : str, side : int, orderQty : int, price : float = None, destination : str = None, myID : str = None, orderType : int = None, **kwargs):
        super().__init__(**kwargs)
        self.msgType = MsgType.NEW.value    
        self.symbol = symbol
        self.side = side
        self.orderQty = orderQty
        self.price = price
        self.ordType = orderType
        self.destination = destination
        self.myID = myID
        
        if not self.ordType:
            if not price:
                self.ordType = OrdType.MARKET.value
            else:
                self.ordType = OrdType.LIMIT.value
        


class CancelOrder(OrderRequest):
    '''
    Convenience message to cancel an order. The only field which needs to be set is routerOrderID.  
    '''
    def __init__(self, routerOrderID: int):
        '''
        The constructor sets self.msgType = MsgType.CANC.value which is required by API to indicate that this is a cancel.
        @param routerOrderID: the order id of order to cancel 
        '''
        super().__init__()
        self.msgType = MsgType.CANC.value
        self.routerOrderID = routerOrderID

        
class ReplaceOrder(OrderRequest):
    '''
    Convenience message to replace an order. For a replace, the only required fields are the routerOrderID and *only* fields whose values need to be
    replaced. Fields whose values are not changing don't need to be set.
    '''
    
    def __init__(self, routerOrderID: int, newPrice: float=None, newQty: int=None, **kwargs):
        '''
        The constructor sets self.msgType = MsgType.REPL.value which is required by API to indicate that this is a replace.
        Replaces typically are for price only, although sometimes also for orderQty. Both arguments are optional. To set other
        order fields to replace, use the kwargs parameter. 
        
        @param routerOrderID: the order id of order to replace
        @param newPrice: new price desired (default=None)
        @param newQty: new orderQty desired (default=None)
        @param @**kwargs: to set other fields as needed 
        '''        
        super().__init__(**kwargs)
        self.msgType = MsgType.REPL.value
        self.routerOrderID = routerOrderID
        self.price = newPrice
        self.orderQty = newQty


from iserver.msgs.SecurityDefinitionRequestApi import SecurityDefinitionRequestApi
from iserver.msgs.SecurityLegInfo import SecurityLegInfo

class ComboSecurityDefinitionRequest(SecurityDefinitionRequestApi):
    def __init__(self, account: str, destination: str, legs: list[SecurityLegInfo], **kwargs):
        """
        Convenience message for a CME-certified COMBO SecurityDefinitionRequest.

        Args:
            account (str): iServer account (must match PartyRequest)
            destination (str): Exchange destination (e.g., 'CME_OPT')
            legs (list): list of SecurityLegInfo, must include at least 2 legs
        """
        super().__init__(**kwargs)
        self.account = account
        self.destination = destination
        self.securitySubType = "COMBO"
        self.legList = legs

