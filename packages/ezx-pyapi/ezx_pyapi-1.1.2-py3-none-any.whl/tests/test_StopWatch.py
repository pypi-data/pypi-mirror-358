'''
Created on 25 Mar 2022

@author: shalomshachne
'''
import unittest
from iserver.util import StopWatch
from time import sleep
from iserver import util


MAX_DELTA_MS = 30

MAX_DELTA_SECS = MAX_DELTA_MS / 1000

MAX_DELTA_NANOS = MAX_DELTA_MS * 1000000

MAX_DELTA_MICROS = MAX_DELTA_NANOS / 1000

class Test(unittest.TestCase):

    def assert_approximately_equals(self, value1, value2, delta=MAX_DELTA_MS):
        value1 = float(value1)
        value2 = float(value2)
        diff = abs(value1 - value2) 
        self.assertTrue(diff <= delta, f'expected diff<{delta}, actual diff={diff}. value={value1}, value2={value2}')

    def setUp(self):
        self.watch = StopWatch()


    def tearDown(self):
        pass

    def testInitialState(self):
        self.assertEqual(0, self.watch.elapsed_nanos())

    def testMeasuresElapsedTime(self):
        sleep_time = .200
        watch = self.watch
        watch.start()
        sleep(sleep_time)
        watch.stop()
        elapsed_nanos = watch.elapsed_nanos()
        self.assertTrue(elapsed_nanos > 0, 'tracked time')
        
        millis = watch.elapsed_millis()
        self.assert_approximately_equals(sleep_time * 1000, millis)
        
    def testMeasuresElapsedTimeSeconds(self):
        sleep_time = .200
        watch = self.watch
        watch.start()
        sleep(sleep_time)
        watch.stop()
        
        seconds = watch.elapsed_seconds()
        self.assert_approximately_equals(sleep_time, seconds, MAX_DELTA_SECS)
        
        
    def testElapsedDataTypes(self):
        sleep_time = .60
        watch = self.watch
        watch.start()
        sleep(sleep_time)
        watch.stop()
        
        value = watch.elapsed_nanos()
        self.assertIsInstance(value, int)        
        
        value = watch.elapsed_micros()
        self.assertIsInstance(value, float)           

        value = watch.elapsed_millis()
        self.assertIsInstance(value, float)      
        
        
        value = watch.elapsed_seconds()
        self.assertIsInstance(value, float)      
                
        
    def testMeasuresElapsedNanosAndMicros(self):
        sleep_time = .090
        watch = self.watch
        watch.start()
        sleep(sleep_time)
        watch.stop()
        
        expected = sleep_time * 1000000000
        nanos = watch.elapsed_nanos()
        self.assert_approximately_equals(expected, nanos, MAX_DELTA_NANOS)
        
        expected = sleep_time * 1000000
        micros = watch.elapsed_micros()
        self.assert_approximately_equals(expected, micros, MAX_DELTA_MICROS)
        
    
    def testStopNotPressedReturnsCurrentElapsed(self):
        sleep_time = .060
        watch = self.watch
        watch.start()
        
        sleep(sleep_time)
        
        expected = sleep_time * 1000
        actual = watch.elapsed_millis()
        self.assert_approximately_equals(expected, actual)
        
        sleep(sleep_time)
        expected *= 2
        actual = watch.elapsed_millis()
        self.assert_approximately_equals(expected, actual)
        
    def testReset(self):
        self.testMeasuresElapsedTime()
        self.watch.reset()
        self.assertEqual(0, self.watch.elapsed_nanos(), 'reset cleared times')
                
    
    def testGetRunningWatch(self):
        watch = util.start_timing()
        self.assertIsNotNone(watch)
        
        self.assertTrue(watch.is_running(), 'started running')
        
    def testIsRunning(self):
        self.assertFalse(self.watch.is_running())
        self.watch.start()
        self.assertTrue(self.watch.is_running())
        self.watch.stop()
        self.assertFalse(self.watch.is_running())
        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()