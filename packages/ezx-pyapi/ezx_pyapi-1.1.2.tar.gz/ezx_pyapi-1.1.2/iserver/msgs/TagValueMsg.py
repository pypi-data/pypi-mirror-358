'''
Created on 18 Feb 2022

@author: SGoldberg
'''
from iserver.EzxMsg import EzxMsg
from iserver.msgs import Field, noop_decode_func


class TagValueMsg(EzxMsg):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.tag_values : dict[str, str] = {}
    
    def update(self, tag:str, value:object):
        self.tag_values[tag] = value
        