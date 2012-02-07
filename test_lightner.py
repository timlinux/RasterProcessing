'''
Created on 07 Feb 2012

@author: timlinux
'''
import os
import unittest
import numpy
from gdal_lightener import (run, screen, darken, lighten)


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testRun(self):
        """Test the lightner function works"""
        myRoot = os.path.abspath(os.path.join(os.path.dirname(__file__)))
        myInfile = os.path.join(myRoot, 'test_in.tif')
        myOutfile = os.path.join(myRoot, 'test_out.tif')
        myAmount = 100
        run(myInfile, myOutfile, myAmount)

    def testScreen(self):
        """Test the screen function works"""
        myValue = 127
        myAmount = 100
        myResult = screen(myValue, myAmount)
        print myResult
        assert myResult == 178

    def testDarken(self):
        """Test the screen function works"""
        myValue = 127
        myAmount = 100
        myResult = darken(myValue, myAmount)
        myMessage = 'Expected 49, got %s' % myResult
        assert myResult == 49, myMessage

    def testLighten(self):
        """Test the lighten function works"""
        myValue = 127
        myAmount = 100
        myResult = lighten(myValue, myAmount)
        myMessage = 'Expected 177, got %s' % myResult
        assert myResult == 177, myMessage

    def testVectorize(self):
        """Test that screen works as a numpy vecorize function"""
        myArray = numpy.array([[0, 1, 2, 127, 255]])
        myFunction = numpy.vectorize(screen)
        myResult = myFunction(myArray, 100)
        assert str(myResult) == '[[100 101 102 178 255]]'


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
