'''
Contains the API field descriptors and mappings to API tags and data types
Created on Sep 29, 2021

@author: Sgoldberg
'''
from iserver.EzxMsg import EzxMsg
from iserver.msgs import Field
from iserver.msgs.field_definitions import api_fields


# this is where one API tag maps to 2 different field objects
_api_tag_collisions = {}

_api_tags = {}
for field in api_fields.values():
    
    if (field.api_tag in _api_tags):  # this is an API Tag collision!
        l = _api_tag_collisions.get(field.api_tag)
        if l == None:
            l = []
            l.append(_api_tags.get(field.api_tag))
            _api_tag_collisions[field.api_tag] = l
        l.append(field)        
       
    _api_tags[field.api_tag] = field

_custom_fields_by_name = {
        'tag_values' : Field('tag_values')
    
    }    


def get_api_field(name):    
    f = api_fields.get(name)
    if not f:
        f = _custom_fields_by_name.get(name)
        
    return f



def get_msg_field(api_tag : str, msg_object : EzxMsg=None):
    try:
        # check collisions first
        fields = _api_tag_collisions.get(api_tag)
        if fields:
            # find the field object which matches a field name on the message
            return next((f for f in fields if msg_object and hasattr(msg_object, f.name)), None)
        # normal case
        return _api_tags[api_tag]
    except:
        return 
    

