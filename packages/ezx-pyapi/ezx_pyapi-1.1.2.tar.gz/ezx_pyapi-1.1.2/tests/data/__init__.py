import random
import string


from iserver.msgs import *
from iserver.msgs import msgtags


class MyMetaClass(type):
    def __new__(cls, clsname, bases, attrs):
        print(f'\ncls={cls}, clsname={clsname}, attrs={attrs}')
        if '__block_fields__' in attrs:
            attrs['__block_fields_by_name__'] = {}
            for field in attrs['__block_fields__'].values():
                attrs['__block_fields_by_name__'][field.name] = field
                print(f'added field={field}')
            
        
        return type(clsname, bases, attrs)
    


class MsgWithBlockFields(object, metaclass=MyMetaClass):
    
        #make static/class level collection since this does not vary by instance.
    __block_fields__ = {
        'EB' : Field('executions', 'EB', noop_decode_func , update_list_item)
        }
    

class Parent(object, metaclass=MyMetaClass):
    pass

class Child(Parent):
    def __init__(self):
        print('Child().__init__()')
        super(Child, self).__init__()

class GrandChild(Child, metaclass = MyMetaClass):
    
        #make static/class level collection since this does not vary by instance.
    __block_fields__ = {
        'EB' : Field('executions', 'EB', noop_decode_func , update_list_item)
        }
    
    def __init__(self):
        print('GrandChild().__init__()')        
        super(GrandChild, self).__init__()
        

def random_symbol(max_chars : int =4) -> string:
    return ''.join(random.choices(string.ascii_uppercase, k=max_chars))

def random_price(min_price : float = .01, max_price : float = 999.99) -> float:
    return round(random.uniform(min_price, max_price), 4)

def random_quantity(min_qty : int = 1, max_qty : int = 5000):
    return random.randint(min_qty, max_qty)

    