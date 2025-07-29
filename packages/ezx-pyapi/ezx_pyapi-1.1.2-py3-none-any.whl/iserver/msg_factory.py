'''
Created on Oct 7, 2021

@author: Sgoldberg
'''
from iserver.EzxMsg import EzxMsg
from iserver.msgs import msgmaps
from iserver.msgs.msgmaps import block_tag_collisions
import logging

logger = logging.getLogger(__name__)

def get_block_message(block_tag : str, parent_msg : EzxMsg) -> EzxMsg :
    '''
    Gets the correct block message object specified by the blockTag. Since the same blockTag could be used
    for different block messages (group in API parlance), make sure to get the block message used by this
    particular parent message.
    
    @param block_tag: the API tag string which identifies the message block
    @param parent_msg: the message which contains the message block.
    @return: a message object found or None
    '''    
   
    if block_tag in block_tag_collisions:
        m = select_block_message_from_collisions(block_tag, parent_msg)    
    else:
        m = msgmaps.msgs_by_block_tag.get(block_tag)
    if m:
        return m()


def select_block_message_from_collisions(block_tag : str, parent_msg : EzxMsg) -> EzxMsg :
    '''
    When the block_field has a name collision, we have to also use the parent/owner message of the field
    to find the right class instance to decode the message.
    '''
    owner_msg = parent_msg.get_block_field_owner(block_tag)
    if owner_msg:
        possible_parents =  block_tag_collisions.get(block_tag)
        return possible_parents.get(owner_msg)


def get_message(msg_subtype : int) -> EzxMsg:
    '''
    Gets a message for the specified message subtype
    
    '''
    try:
        m = msgmaps.msgs_by_subtype[msg_subtype]
        return m()
    except KeyError:
        return  # this is okay. just bad msgType.
    except Exception as e:
        logger.exception(f'Exception creating message for subtype={msg_subtype}. e={e}')
        return 

