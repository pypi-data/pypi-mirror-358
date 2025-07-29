from _io import StringIO
import io

from iserver import msg_factory
from iserver.EzxMsg import EzxMsg
from iserver.msgs import msgtags

# API constants for delimiters in messages
TAG_VALUE_PAIRS_DELIMITER = '\001'
TAG_VALUE_SEPARATOR = '='
END_MESSAGE_DELIMITER = '\003'

# API doubles are sent as strings. Max decimals transmitted = 8
_DOUBLE_FORMAT = ".8g"          


def zero_pad(value, digits):
    return str(value).zfill(digits)



def to_string(value):
    if isinstance(value, float):
        return format(value, _DOUBLE_FORMAT)
    return str(value)


def msg_to_map(msg):
    d = dict()
    if len(msg) > 0 and msg[-1] == END_MESSAGE_DELIMITER:
        msg = msg[0:-1]
    for pair in msg.split(TAG_VALUE_PAIRS_DELIMITER):
        if TAG_VALUE_SEPARATOR in pair:
            d.update([pair.split(TAG_VALUE_SEPARATOR)])
    return d

'''
Decode received text to the appropriate API message (as determined by the msg_subtype value). If invalid msg_subtype,
returns None (and does not throw an error).
 
Created on Oct 5, 2021

@author: Sgoldberg
'''  


def decode_message(msg_subtype: int, msg: str):
    '''
    Decode a message received from the API
    @param msg_subtype: int which defines what type of message was received.  See IserverMsgSubType
    @param msg: a text message (decoded from bytes received from in the ApiClient socket). 
    '''
    m = msg_factory.get_message(msg_subtype)    
    if not m:
        return
    
    return populate_message(m, msg)
#     for tag_values in msg.split(TAG_VALUE_PAIRS_DELIMITER):
#         msg_field = None        
#         for item in tag_values.split(TAG_VALUE_SEPARATOR):
#             if not msg_field:
#                 msg_field = msgtags.get_msg_field(item, m)
#                 if not msg_field:
#                     break
#             else:
#                 msg_field.update_msg_field(m, item)
#             
#     return m    


def populate_message(m: EzxMsg, msg: str, start_index: int=None, end_index: int=None):
    '''
    Populate the specified EzxMsg object with values read from the received message string. For a message string within the message, 
    specify start_index and end_index parameters to parse the submessage only.
    
    @param m: a message object to populate
    @param msg: text received to decode into the message object
    @param start_index: optional index of where to start parsing the message string (defaults to beginning of the string)
    @param end_index: optional end index where to end parsing (defaults to end of the string)    
    '''
    tag_buffer = StringIO()
    value_buffer = StringIO()
    tag = None
    value = None
    
    msg_field = None     
    i = start_index or 0   
    stop = end_index or len(msg)
    while i < stop:
        c = msg[i]
        # increment here (TODO: explain why - has to do with return from parse_block)
        i = i + 1   
        
        # it's possible that a state variable would make this easier to understand. There are 2 states:
        #    1. reading the Tag name - signaled by start of the message or completing reading last value (hit the \x001 delimiter
        #    2. reading the value - signaled by reading an '=' sign at the end of the tag name.
        
        if c == TAG_VALUE_SEPARATOR and tag == None:  # if we already have the tag defined, then this '=' character is inside the value
            tag = tag_buffer.getvalue()      
            msg_field = msgtags.get_msg_field(tag, m)            
            
        elif c == TAG_VALUE_PAIRS_DELIMITER:
            value = value_buffer.getvalue()
            if 'B' == tag:  # indicates we have a sub-message (message block/group) contained within the message.
                i, *_ = parse_block(i, msg, m, value)  # read just the submessage section and continue at the next tag not in the submessage
                        
            elif msg_field: 
                msg_field.update_msg_field(m, value)
            
            else:  # last chance method, used to update custom messages
                m.update(tag, value)

            # reset buffers for next tag/value                
            tag_buffer.close()
            tag_buffer = StringIO()
            tag = None
            value_buffer.close()
            value_buffer = StringIO()
            msg_field = None
            
        elif msg_field == None and tag == None:
            tag_buffer.write(c)
            
        else:
            value_buffer.write(c)
                
    return m   

'''
Parse subsequence of the message into another message object and update the parent message object 
with the result.
@param start_index: start index for in message
@param msg: the text received from API
@param msg_object: the parent msg which contains the message block (sub message) 
@param block_id:   the string which identifies what kind of message the block represents
@return: return index in string for next character to read.   
'''


def parse_block(start_index: int, msg: str, msg_object: EzxMsg, block_id: str) -> int:
    end_text = f'E={block_id}\001'
    block_end = msg.find(end_text, start_index) 
    # TODO: handle bad message where block_end = -1
    block_msg = msg_factory.get_block_message(block_id, msg_object)    
    if block_msg:
        populate_message(block_msg, msg, start_index, block_end) 
        block_field = msg_object.get_block_field(block_id)
        if block_field:
            block_field.update_msg_field(msg_object, block_msg)
        # TODO: figure out how to update the base message with the block message
        # e.g. msg_factory.get_block_field(msg_object, block_id)
            
    return block_end + len(end_text), block_msg


def populate_message2(m, msg):
    for tag_values in msg.split(TAG_VALUE_PAIRS_DELIMITER):
        msg_field = None        
        for item in tag_values.split(TAG_VALUE_SEPARATOR):
            if not msg_field:
                msg_field = msgtags.get_msg_field(item, m)
                if not msg_field:
                    break
            else:
                msg_field.update_msg_field(m, item)
            
    return m    

        
def decode_block(block_tag: str, msg_fragment: str):
    m = msg_factory.get_block_message(block_tag)
    if not m:
        return
    

def parse_header(header: bytearray):
    # TODO: check length?
    header = header.decode('UTF-8')
    msg_length = int(header[0:6])
    msg_type = int(header[6:8])
    msg_subtype = int(header[8:11])
    return (msg_length, msg_type, msg_subtype)
    
    
def encode(msg: EzxMsg) -> str: 
    '''
    Encode the specified message a text string of name/value pairs (according to the API encoding) 
    '''
    msg_buffer = io.StringIO()    
    encode_buffer(msg, msg_buffer)
    return msg_buffer.getvalue()


def encode_buffer(msg: str, buffer: StringIO):
    '''
        Encode the specified message a text string of name/value pairs (according to the API encoding) into the specified StringIO buffer  
    '''
    for field_name, value in vars(msg).items(): 
        if value == None:
            continue
        isBlock = True
        f = msg.get_block_field_by_name(field_name)
        if not f:
            f = msgtags.get_api_field(field_name)
            isBlock = False
        if not f:
            continue
        
        encode_field(msg, buffer, f, value, isBlock)


def encode_tag_value(buffer, value, tag):
    buffer.write(tag)
    buffer.write(TAG_VALUE_SEPARATOR)
    buffer.write(to_string(value))
    buffer.write(TAG_VALUE_PAIRS_DELIMITER)


def encode_field(msg, buffer, field, value, isBlock):
        if (type(value) == list):
            for item in value: encode_field(msg, buffer, field, item, isBlock)
            return
        
        # dictionary is a field in a custom message (TagValueMsg) it is not a standard API object type (yet)
        if (type(value) == dict):
            for tag, item_value in value.items():
                encode_tag_value(buffer, item_value, tag)
            return
            
        if isBlock:
            # the value is a message, write the Start block Tag/Value
            encode_tag_value(buffer, field.api_tag, 'B')
            # encode the full message
            encode_buffer(value, buffer)
            # write the End block Tag/Value            
            encode_tag_value(buffer, field.api_tag, 'E')
            return
                        
        tag = field.api_tag
        encode_tag_value(buffer, value, tag)        

    
def header(msg_length: int, msg_type: int, msg_subtype: int, seqno: int, buffer: io.StringIO):
    buffer.write(zero_pad(msg_length + 1, 6))  # add ETX character
    buffer.write(zero_pad(msg_type, 2))
    buffer.write(zero_pad(msg_subtype, 3))
    buffer.write(zero_pad(seqno, 3))
    buffer.write(TAG_VALUE_PAIRS_DELIMITER)




def to_api_msg(msg: EzxMsg, seqno: int=0) -> str:
    '''
    Generate an API message from the specified object. This will start with 15 byte 
    API Header and end with API END_MESSAGE_DELIMITED (Ascii 3)
    '''        
    api_buffer = io.StringIO() 
    msg_buffer = io.StringIO()           
    encode_buffer(msg, msg_buffer)
    # print(f'msg_buffer={msg_buffer.getvalue()}')
    header(msg_buffer.tell(), msg.msg_type, msg.msg_subtype, seqno, api_buffer)
    api_buffer.write(msg_buffer.getvalue())
    api_buffer.write(END_MESSAGE_DELIMITER)
    return api_buffer.getvalue()


def to_api_bytes(msg: EzxMsg, seqno: int=0) -> bytearray:
    return to_api_msg(msg, seqno).encode(encoding='UTF-8')
    


