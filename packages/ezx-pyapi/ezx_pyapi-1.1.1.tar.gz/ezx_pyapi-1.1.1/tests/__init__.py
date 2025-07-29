import logging.config
import os
from random import randint
import random
import string
import unittest
import time
from time import sleep


_RAND_STR_LENGTH = 10

my_path = os.path.dirname(__file__)
logging.config.fileConfig(f'{my_path}/logging.ini')

def check_logging():
    return True

def random_string(size = _RAND_STR_LENGTH):
    return "".join(random.choices(string.ascii_letters, k=size))

def random_number(smallest=0, largest=999999):
    return randint(smallest, largest)

def assert_fields_match(expected, actual, test_case: unittest.TestCase):
    '''
    Compare 2 objects based on their attributes. If all attributes are equal, assertion passes
    '''
    attrs1 = set(vars(expected).items())
    attrs2 = set(vars(actual).items())
    missing_from_actual = attrs1 - attrs2
    in_actual_not_in_expected = attrs2 - attrs1
    actual_diffs, expected_diffs = len(missing_from_actual), len(in_actual_not_in_expected)
    error = ""
    if (actual_diffs > 0):
        error = "actual not equal: {0}".format_order(missing_from_actual)
    if (expected_diffs > 0):
        error = error + ", in actual not in expected: {0}".format_order(in_actual_not_in_expected)
    test_case.assertEqual(0, actual_diffs + expected_diffs, error)
    
def wait_for_condition(predicate, max_wait_secs : float = 30, sleep_secs: float = .030):    
    '''
    Wait for specified predicate to be true, until a maximum time has elapsed.
    @param predicate: a function which returns true or false 
    @param max_wait_secs: maximum time to wait until condition is true
    @param sleep_secs: sleep interval while waiting. default=.03. A value of 0 means processor spins until done waiting. 
    '''
    start = time.time()
    while not predicate() and time.time() - start <= max_wait_secs:
        sleep(sleep_secs)
    
def fill_array(dest, source) -> int:
    objects = min(len(dest), len(source))
    for i in range(0, objects, 1):
        dest[i] = source[i]       

    return objects
    