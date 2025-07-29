import logging

logger = logging.getLogger(__name__)


class Field:
    '''
    Field descriptor for API message fields.  API messages are sent as strings of name/value pairs. The name is referred to as the API tag.
    
    Attributes:
        api_tag (str): The API tag used for this field. For example:  DEST (for the destination field)
        from_string (function): a function which can convert the string representation of the value to the correct data type. Used for decoding received messages. Default= str
        update_func (function): a function to update the corresponding attribute in the message with the field value. Default = setattr. The other function used is msgs.update_list_item
            if the message attribute is a list object.
    '''

    
    def __init__(self, name=None, api_tag=None, decode_func=str, update_func=setattr):
        '''
        Constructor 
        
        Parameters:
            name (str): Field name/attribute name in the message class
            api_tag (str): the API tag string which identifies the field in the message
            
        
        '''
        self.name = name
        self.api_tag = api_tag
        self.from_string = decode_func
        self.update_func = update_func
                
    def __str__(self):
        return f'Field: name={self.name}, api_tag={self.api_tag}'
    
    def decode_value(self, value):
        return self.from_string(value)
    
    def update_msg_field(self, msg_obj, value):
        # setattr(m, msg_field.name, value)
        self.update_func(msg_obj, self.name, self.decode_value(value))


def noop_decode_func(value):
    '''
        Placeholder function for fields that don't have a decode logic
    '''    
    return value


def update_list_item(obj, property_name, item_value):
    '''
    Fields which are lists of objects use this as their update function.  This will add the specified item_value to the list specified by property_name.
    '''        
    l = getattr(obj, property_name)
    if not l:
        l = []
        setattr(obj, property_name, l)    
    l.append(item_value)    


__all__ = [ 'Field','noop_decode_func' ,'update_list_item' ]

# do not move these import statements
from .ClientOrderResponse import ClientOrderResponse
from .ClientOrderStatus import ClientOrderStatus
from .ExecutionStatus import ExecutionStatus
from .LogonRequest import LogonRequest
from .LogonResponse import LogonResponse
from .OrderResponse import OrderResponse
from .OrderStatus import OrderStatus
from .SecurityDefinitionRequestApi import SecurityDefinitionRequestApi
from .SecurityDefinitionResponseApi import SecurityDefinitionResponseApi
from .SecurityLegInfo import SecurityLegInfo
from .RequestForQuoteApi import RequestForQuoteApi






