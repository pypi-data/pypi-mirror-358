'''
Created on Oct 6, 2021

@author: Sgoldberg
'''
import iserver


'''
Metaclass for all EzxMsg subclasses to implement whatever common setup code is needed
'''
class EzxMsgMeta(type):
    
    '''
        optionally create the __block_fields_by_name dictionary if __block_fields__ is defined
    '''
    def __new__(cls, clsname, bases, attrs):        
        if '__block_fields__' in attrs:
            attrs['__block_fields_by_name__'] = {}
            for field in attrs['__block_fields__'].values():
                attrs['__block_fields_by_name__'][field.name] = field                
            
        
        return type(clsname, bases, attrs)


'''
classdocs
'''
class EzxMsg(object):

    def __init__(self, **kwargs):
        iserver.set_properties(self, kwargs)
    
    def __eq__(self, other):
        return iserver.msg_equals(self, other)
        
    def __str__(self):
        return iserver.to_bean_string(self)
    
    def __repr__(self):
        return iserver.to_bean_string(self, iserver._all_props_filter)
    

    def get_block_field(self, api_block_tag : str):
        '''
        When decoding a received message, if there is a "block" found in the message, get a Field for the specified block tag. Returns none
        if this EzxMsg subtype does not contain a field for this block.
        
        @param api_block_tag: the API tag name which corresponds to the block field we are looking for
        @return: the Field definition or None if not found
        '''
                
        found = self.do_block_field_lookup(api_block_tag)
        if found:
            return found[1]
                

    def get_block_field_by_name(self, field_name : str):
        '''
        When encoding, we need to see whether the specified messge field (field_name parameter)
        is a block field -- in which it is encoded as a message, or whether it is a simple field --
        in which case it is encoded as single text value.  Will return None if the field_name is 
        not a block field    
        '''        
        # so ... the field we are looking for could be defined in a super class of the current instance
        # therefore we iterate the class heirarchy of the object to check each class for existence of the field we are looking
        # for.        
        mro = self.__class__.__mro__
        for t in mro:            
            try:
                f = t.__block_fields_by_name__.get(field_name)
                if f:
                    return f
            except AttributeError:
                pass
        
    
    def get_block_field_owner(self, api_block_tag: str):
        found = self.do_block_field_lookup(api_block_tag)
        if found:
            return found[0]
 
            

    def do_block_field_lookup(self, api_block_tag: str):
        # so ... the field we are looking for could be defined in a super class of the current instance
        # therefore we iterate the class heirarchy of the object to check each class for existence of the field we are looking
        # for.        
        mro = self.__class__.__mro__
        for t in mro:            
            try:
                f = t.__block_fields__.get(api_block_tag)
                if f:
                    return t,f
            except AttributeError:
                pass
            
    
    def update(self, tag : str, value : object):
        '''
        Optional method to update this message object from the tag/value pair. This would be used for custom messages
        which do not have their fields identified in the iserver.msgs.field_definitions module.
        
        @param tag: API tag which identifies the field to update
        @param value: value to assign t the field  
        '''
        pass # no-op, mean to be overridden in subclasses
    
    def get_seqNo(self) -> int:
        '''
        Gets the API sequence number of this message. 
        '''
        if hasattr(self, 'seqNo'):  #seqNo is not defined in all API messages, but when it is, it should be stored
            return self.seqNo
        
    