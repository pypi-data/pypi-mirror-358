'''
Created on Sep 29, 2021

@author: Sgoldberg
'''
import unittest

from iserver.msgs import msgtags
from iserver.msgs.LogonResponse import LogonResponse
from iserver.msgs.OrderResponse import OrderResponse
from iserver.msgs import Field, update_list_item
from tests import random_string, random_number


class Test(unittest.TestCase):


    def testMsgTags(self):
        f = msgtags.get_api_field('companyName')
        self.assertIsNotNone(f, "got companyName field")

    def test_field_decode_string(self):
        f = Field('field1', 'FNAM')
        value = random_string()
        result = f.decode_value(value)
        self.assertEqual(value, result)
        
    def test_field_decode_int(self):
        f = Field('logonType', 'TYPE', int)
        value = str(random_number(0, 10))
        result = f.decode_value(value)
        self.assertEqual(int(value), result)
        
    def test_field_update_string(self):
        m = LogonResponse()
        f = Field('returnCode', 'RETC', int)
        value = "0"
        f.update_msg_field(m, value)
        self.assertEqual(0, m.returnCode)
        
    def test_field_update_list_attribute(self):
        m = LogonResponse()
        self.assertIsNone(m.destinations)
        f = Field('destinations', 'DEST', update_func = update_list_item)
        value = "SIMU1"
        f.update_msg_field(m, value)
        self.assertEqual(1, len(m.destinations))
        self.assertEqual(value, m.destinations[0])
        
    def test_name_collisions(self):
        self.assertTrue('DEST' in msgtags._api_tag_collisions)
        fields = msgtags._api_tag_collisions.get('DEST')
        self.assertEqual(2, len(fields))
        f = fields[0]
        self.assertEqual('destinations', f.name)
        f = fields[1]
        self.assertEqual('destination', f.name)
    
    def test_get_api_field_which_has_collision(self):
        api_tag = 'DEST'
        mo = LogonResponse()
        f = msgtags.get_msg_field(api_tag, mo)
        self.assertIsNotNone(f)
        self.assertEqual('destinations', f.name)

        mo = OrderResponse()
        f = msgtags.get_msg_field(api_tag, mo)
        self.assertIsNotNone(f)
        self.assertEqual('destination', f.name, "got the OrderResponse field definition")

        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()