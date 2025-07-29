'''
Created on 22 Feb 2022

@author: shalomshachne
'''
import unittest

from iserver import parse_to_dict


class Test(unittest.TestCase):

    def test_parse_to_dict_with_good_string(self):
        values = 'key1=1645193523396-2key2=1645193523396-3'
        d = parse_to_dict(values)        
        
        self.assertIsNotNone(d)
        key = 'key1'
        expected = '1645193523396-2'
        actual = d.get(key)
        self.assertEqual(expected, actual, key)
        
        key = 'key2'
        expected = '1645193523396-3'
        actual = d.get(key)
        self.assertEqual(expected, actual, key)
        
    def test_parse_to_dict_specify_pairs_separator(self):
        pair_separator = ','
        values = 'key1=1645193523396-2,key2=1645193523396-3'
        d = parse_to_dict(values, pair_separator)        
        
        self.assertIsNotNone(d)
        key = 'key1'
        expected = '1645193523396-2'
        actual = d.get(key)
        self.assertEqual(expected, actual, key)
        
        key = 'key2'
        expected = '1645193523396-3'
        actual = d.get(key)
        self.assertEqual(expected, actual, key)       
        
    def test_parse_to_dict_specify_name_value_separator(self):
        pair_separator = ','
        name_value_separator = '|'
        values = 'key1|1645193523396-2,key2|1645193523396-3'
        d = parse_to_dict(values, pair_separator, name_value_separator)        
        
        self.assertIsNotNone(d)
        key = 'key1'
        expected = '1645193523396-2'
        actual = d.get(key)
        self.assertEqual(expected, actual, key)
        
        key = 'key2'
        expected = '1645193523396-3'
        actual = d.get(key)
        self.assertEqual(expected, actual, key)        
        
    def test_parse_to_dict_specify_name_value_separator_strips_white_space(self):
        pair_separator = ','
        name_value_separator = '|'
        values = 'key1|1645193523396-2 , key2|1645193523396-3'
        d = parse_to_dict(values, pair_separator, name_value_separator)        
        
        self.assertIsNotNone(d)
        key = 'key1'
        expected = '1645193523396-2'
        actual = d.get(key)
        self.assertEqual(expected, actual, key)
        
        key = 'key2'
        expected = '1645193523396-3'
        actual = d.get(key)
        self.assertEqual(expected, actual, key)        
        
    def test_extra_token(self):
        values = 'key1=1645193523396-2key2=1645193523396-3'
        d = parse_to_dict(values)        
        
        self.assertIsNotNone(d)
        key = 'key1'
        expected = '1645193523396-2'
        actual = d.get(key)
        self.assertEqual(expected, actual, key)
        
        key = 'key2'
        expected = '1645193523396-3'
        actual = d.get(key)
        self.assertEqual(expected, actual, key)               


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.test_parse_to_dict_with_good_string']
    unittest.main()
