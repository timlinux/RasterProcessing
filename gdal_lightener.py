"""
Raster lightner tool.

Contact : Tim Sutton (tim@linfiniti.com)

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

.. todo:: Implement as a QGIS plugin

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.1.0'
__date__ = '-7/02/2012'
__copyright__ = ('Copyright 2012, Linfiniti Consulting cc.')
from osgeo import gdal
from osgeo.gdalconst import (GDT_Byte, GA_ReadOnly)
import sys
import numpy


def usage():
    print('usage: gdal_lightener.py [-q] [-of file_format] -a amount src_color'
          ' dst_color\n\n'
          'where\n'
          'amount is the amount of lightening to apply [0-255]\n'
          'src_color is a RGB or RGBA dataset\n',
          'dst_color will be a RGB or RGBA dataset\n'
          '\n'
          'Use a lower amount to get a darker image (closer to original)')
    sys.exit(1)


def lighten(theSourceFilename,
            theDestinationFilename,
            theAmount=100,
            theFileFormat='GTiff',
            theQuietFlag=False):
    """Function to lighten the pixel intensity of a raster in
    order to give it a 'washed out' appearance.
    Input

        * theDestinationFilname - output filename
        * theSourceFileName - input filename
        * theAmount - intensity of lightening to apply [0-255]
                    Defaults to 100
        * theFileFormat - Output format (defaults to geotiff)
        * theQuietFlag - whether to show progress in terminal
                    Defaults to False

    Output
        Writes output file to disk, returns nothing
    Exception
        Throws exception should any error occur
    """
    myDataType = GDT_Byte

    myInputDataset = gdal.Open(theSourceFilename, GA_ReadOnly)

    #check for 3 or 4 bands in the color file
    if (myInputDataset.RasterCount != 3 and myInputDataset.RasterCount != 4):
        myMessage = ('Source image does not appear to have three or'
                    'four bands as required.')
        raise Exception(myMessage)

    #define output file_format, name, size, type and set projection
    myOutputDriver = gdal.GetDriverByName(theFileFormat)
    myOutputDataset = myOutputDriver.Create(theDestinationFilename,
                                            myInputDataset.RasterXSize,
                                            myInputDataset.RasterYSize,
                                            myInputDataset.RasterCount,
                                            myDataType)
    myOutputDataset.SetProjection(myInputDataset.GetProjection())
    myOutputDataset.SetGeoTransform(myInputDataset.GetGeoTransform())

    #assign RGB and colorshade bands
    myRedBand = myInputDataset.GetRasterBand(1)
    myGreenBand = myInputDataset.GetRasterBand(2)
    myBlueBand = myInputDataset.GetRasterBand(3)
    myAlphaBand = None
    if myInputDataset.RasterCount == 4:
        myAlphaBand = myInputDataset.GetRasterBand(4)

    myXSize = myRedBand.XSize
    myYSize = myRedBand.YSize

    # Set up a numpy vectorize function that will iteratively
    # apply the function to each numpy array element
    myFunction = numpy.vectorize(screen)

    #loop over lines to apply colorshade
    for myRow in range(myYSize):
        #load RGB and colorshade arrays
        myRedScanline = myRedBand.ReadAsArray(
                                            0, myRow, myXSize, 1, myXSize, 1)
        myGreenScanline = myGreenBand.ReadAsArray(
                                            0, myRow, myXSize, 1, myXSize, 1)
        myBlueScanline = myBlueBand.ReadAsArray(
                                            0, myRow, myXSize, 1, myXSize, 1)
        myAlphaScanline = None
        if myAlphaBand is not None:
            myAlphaScanline = myAlphaBand.ReadAsArray(
                                            0, myRow, myXSize, 1, myXSize, 1)

        # Now apply it to our r,g,b bands
        myRedScanline = myFunction(myRedScanline, theAmount)
        myGreenScanline = myFunction(myGreenScanline, theAmount)
        myBlueScanline = myFunction(myBlueScanline, theAmount)
        #print 'After:', myBlueScanline
        #write out new RGB bands to output one band at a time
        myOutputBand = myOutputDataset.GetRasterBand(1)
        myOutputBand.WriteArray(myRedScanline, 0, myRow)
        myOutputBand = myOutputDataset.GetRasterBand(2)
        myOutputBand.WriteArray(myGreenScanline, 0, myRow)
        myOutputBand = myOutputDataset.GetRasterBand(3)
        myOutputBand.WriteArray(myRedScanline, 0, myRow)
        if myAlphaBand is not None:
            myOutputBand = myOutputDataset.GetRasterBand(4)
            myOutputBand.WriteArray(myAlphaScanline, 0, myRow)

        #update progress line
        if not theQuietFlag:
            gdal.TermProgress_nocb((float(myRow + 1) / myYSize))


def screen(thePixelValue, theAmount=100):
    """An implementation of the 'screen' image processing procedure.
    .. see:: http://en.wikipedia.org/wiki/Blend_modes#Screen
    Input

        * thePixelValue - a value in the range [0-255]
        * theAmount - intensity of lightening to apply [0-255]
                    defaults to 100

    Output
        A value with the 'screen' effect applied to it
    Exception
        none
    """
    return(255 - (((255 - theAmount) * (255 - thePixelValue)) / 255))


if __name__ == '__main__':
    argv = gdal.GeneralCmdLineProcessor(sys.argv)
    if argv is None:
        sys.exit(0)

    myFileFormat = 'GTiff'
    mySourceFilename = None
    myDestinationFilename = None
    myAmount = 200  # default
    myQuietFlag = False

    # Parse command line arguments.
    myArgument = 1
    while myArgument < len(argv):
        arg = argv[myArgument]

        if arg == '-of':
            myArgument = myArgument + 1
            myFileFormat = argv[myArgument]

        elif arg == '-q' or arg == '-myQuietFlag':
            myQuietFlag = True

        if arg == '-a':
            myArgument = myArgument + 1
            myAmount = int(argv[myArgument])
            if myAmount < 0 or myAmount > 255:
                myMessage = 'invalid range for amount - use [0-255]'
                print myMessage
                sys.exit(1)

        elif mySourceFilename is None:
            mySourceFilename = argv[myArgument]

        elif myDestinationFilename is None:
            myDestinationFilename = argv[myArgument]
        else:
            usage()
        myArgument = myArgument + 1

    if myDestinationFilename is None:
        usage()

    lighten(mySourceFilename,
            myDestinationFilename,
            myAmount,
            myFileFormat,
            myQuietFlag)
