import io
import logging

API_HEADER_SIZE = 15

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def _all_props_filter(key_value):
    return True

   
def msg_equals(msg1, msg2) -> bool:
    if not isinstance(msg1, type(msg2)):
        return False
    
    for name,value in vars(msg1).items():
        if getattr(msg2, name) != value:
            return False

    return True

def to_bean_string(obj, property_filter=lambda name_value: name_value[1] != None):
    '''
    Print the objects properties. The optional property_filter should be a function which can be used
    to filter 2 element tuples (name, value).  By default, this will filter out blank values.
    @author: Sgoldberg
    '''   
    properties_of_interest = list(filter(property_filter, vars(obj).items()))
    buffer = io.StringIO()
    for name,value in properties_of_interest:
        if buffer.tell() > 0: 
            buffer.write(', ')
        buffer.write(f'{name}={value}')
    return buffer.getvalue()


def set_properties(obj : object, properties : dict):
    '''
    Set object properties from the specified dictionary. No type conversion is done.
    '''
    for name,value in properties.items():
        try:
            setattr(obj, name, value)
        except:
            pass

def parse_to_dict(name_value_pairs: str, pair_separator: str = '\001', name_value_separator : str = '=') -> dict:
    '''
    Parse a string into a dictionary
    @param name_value_pairs: set of paired values where a list of keys and values can be parsed
    @param pair_separator: the delimiter which separates each name value pair, for example ','   
    @param name_value_separator: the delimiter which separates each name and value, for example '=' (default)
    '''
    d = dict()
    # not using generator in dict() constructor to allow for irregularities. For example if the input string has an extra
    # delimiter at the end.
    for name_value in (pairs.split(name_value_separator) for pairs in name_value_pairs.split(pair_separator)):
        if len(name_value) > 1:
            d[name_value[0].strip()] = name_value[1].strip()
            
    return d


