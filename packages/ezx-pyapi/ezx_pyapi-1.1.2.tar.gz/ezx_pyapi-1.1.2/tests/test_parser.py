'''
Created on 29 Apr 2022

@author: shalomshachne
'''
import unittest
import argparse



class Test(unittest.TestCase):


    def testParserExit(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('side', type=str)
        parser.add_argument('symbol', type=str)
        for action in parser._actions: action.required = False
        args = ['B']
        
        r = parser.parse_args(args)
        self.assertIsNotNone(r)
        
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testParserExit']
    unittest.main()