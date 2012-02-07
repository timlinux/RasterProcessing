'''
Created on 07 Feb 2012

@author: timlinux
'''
import os
import unittest
from gdal_lightener import (lighten, processScanline, screen)


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testLightner(self):
        """Test the lightner function works"""
        myRoot = os.path.abspath(os.path.join(os.path.dirname(__file__)))
        myInfile = os.path.join(myRoot, 'test_in.tif')
        myOutfile = os.path.join(myRoot, 'test_out.tif')
        myAmount = 100
        lighten(myAmount, myInfile, myOutfile)

    def testProcessScanline(self):
        """Test the processScanline function works"""
        myArray = [255, 127, 1]
        myAmount = 100
        myResult = processScanline(myAmount, myArray)
        print myResult
        assert str(myResult) == '[255, 178, 101]'
        #actual data from our test raster...
        myArray = [199, 155, 166, 223, 161, 138, 214, 224, 0, 0, 0, 0, 0, 236]
        myResult = processScanline(myAmount, myArray)
        print myResult
        assert (str(myResult) == ('[221, 195, 201, 236, 198, 184, 231,'
                             ' 237, 100, 100, 100, 100, 100, 244]'))

    def testScreen(self):
        """Test the screen function works"""
        myValue = 127
        myAmount = 100
        myResult = screen(myAmount, myValue)
        print myResult
        assert myResult == 178

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
