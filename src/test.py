import unittest
import numpy as np
from scipy import misc

from normalize import normalizeMeanVariance
from region_of_interest import getRoi
from ridge_orientation import ridgeOrient
from ridge_frequency import ridgeFreq
from filters import gaborFilter
from lib import splitFilename
import exceptions as ex

class TestImageManipulationFunctions(unittest.TestCase):
    def setUp(self):
        # generate valid test image
        self.im = np.arange(256, dtype=np.uint8)
        self.im = np.tile(self.im, (300,1))

        # generate invalid (rgb) test image
        self.im_color = np.ones((300,256,3), dtype=np.uint8) * 128

        # generate list of invalid datatypes
        self.invalidDTypes = [1, 1.0, "str", (1,"2"), [1, "2"], None, True]

        # generate list of non-numerical datatypes
        self.nonNum = ["1", (1,1), [1,1], np.array([1]), np.ones((1)), None] # don't add boolean - is instance of int

        # generate list of non-bool datatypes
        self.nonBool = [1, 1.0, "1", (1,1), [1,1], np.array([1]), np.ones((1)), None]

class TestDatatypes(TestImageManipulationFunctions):
    def testNormalization_invalid(self):
        for item in self.invalidDTypes:
            with self.assertRaises(ex.InvalidDataType):
                normalizeMeanVariance(item)
    
    def testRoi_invalid(self):
        for item in self.invalidDTypes:
            with self.assertRaises(ex.InvalidDataType):
                getRoi(item)
    
    def testOrientation_invalid(self):
        for item in self.invalidDTypes:
            with self.assertRaises(ex.InvalidDataType):
                ridgeOrient(item)

    def testFrequency_invalid(self):
        orientim = ridgeOrient(self.im)

        for item in self.invalidDTypes:
            # invalid image, valid orientations
            with self.assertRaises(ex.InvalidDataType):
                ridgeFreq(item, orientim)
            
            # valid image, invalid orientations
            with self.assertRaises(ex.InvalidDataType):
                ridgeFreq(self.im, item)

            # both params invalid
            with self.assertRaises(ex.InvalidDataType):
                ridgeFreq(item, item)

    def testGabor_invalid(self):
        orientim = ridgeOrient(self.im)
        freq = ridgeFreq(self.im, orientim)
        mask = getRoi(self.im)

        for item in self.invalidDTypes:
            # invalid original image
            with self.assertRaises(ex.InvalidDataType):
                gaborFilter(item, orientim, freq, mask)

            # invalid orientation image
            with self.assertRaises(ex.InvalidDataType):
                gaborFilter(self.im, item, freq, mask)

            # invalid frequency image
            with self.assertRaises(ex.InvalidDataType):
                gaborFilter(self.im, orientim, item, mask)
                
            # invalid mask
            with self.assertRaises(ex.InvalidDataType):
                gaborFilter(self.im, orientim, freq, item)

class TestDimensions(TestImageManipulationFunctions):
    def testNormalization_invalid(self):
        with self.assertRaises(ex.InvalidInputImageDimensions):
            normalizeMeanVariance(self.im_color)

    def testRoi_invalid(self):
        with self.assertRaises(ex.InvalidInputImageDimensions):
            getRoi(self.im_color)

    def testOrientation_invalid(self):
        with self.assertRaises(ex.InvalidInputImageDimensions):
            ridgeOrient(self.im_color)
    
    def testFrequency_invalid(self):
        orientim = ridgeOrient(self.im)
        
        with self.assertRaises(ex.InvalidInputImageDimensions):
            ridgeFreq(self.im_color, orientim)

        with self.assertRaises(ex.InvalidInputImageDimensions):
            ridgeFreq(self.im, self.im_color)

    def testGabor_invalid(self):
        orientim = ridgeOrient(self.im)
        freq = ridgeFreq(self.im, orientim)
        mask = getRoi(self.im)

        with self.assertRaises(ex.InvalidInputImageDimensions):
            gaborFilter(self.im_color, orientim, freq, mask)
        
        with self.assertRaises(ex.InvalidInputImageDimensions):
            gaborFilter(self.im, self.im_color, freq, mask)

        with self.assertRaises(ex.InvalidInputImageDimensions):
            gaborFilter(self.im, orientim, self.im_color, mask)
        
        with self.assertRaises(ex.InvalidInputImageDimensions):
            gaborFilter(self.im, orientim, freq, self.im_color)

class TestOptionalParams(TestImageManipulationFunctions):
    def testRoi_invalid(self):
        for item in self.nonNum:
            with self.assertRaises(ex.InvalidDataType):
                getRoi(self.im, threshold=item)

    def testOrientation_invalid(self):
        for item in self.nonBool:
            with self.assertRaises(ex.InvalidDataType):
                ridgeOrient(self.im, flip=item)
    
    def testFrequency_invalid(self):
        orientim = ridgeOrient(self.im)
        
        #non-numeric and non-None
        invalidParams = ["1", (1,1), [1,1], np.array([1]), np.ones((1))]

        for item in invalidParams:
            with self.assertRaises(ex.InvalidDataType):
                ridgeFreq(self.im, orientim, blend_sigma=item)

    def testGabor_invalid(self):
        orientim = ridgeOrient(self.im)
        freq = ridgeFreq(self.im, orientim)
        mask = getRoi(self.im)

        # non-int
        invalidParams = [1.0, "1", (1,1), [1,1], np.array([1]), np.ones((1)), None]
        for item in invalidParams:
            with self.assertRaises(ex.InvalidDataType):
                gaborFilter(self.im, orientim, freq, mask, blocksize=item)

class testFilenameSplitting(unittest.TestCase):
    def setUp(self):
        self.noExtension = ["filename", "file name", ".", "..", ". .", "....",  "... ."]
        self.validFilename = ["file.name", "file.n.ame", " file.n.ame", "fil e.n.ame", "file. n.ame", "..name", ". .name", "....name"]
        self.invalidFilename = ["", "file. name", "file.n ame", "file.na me", "file.name ", "file.n. ame", ".. name", "..name ",
                            ".. name ", ".... name", ".... na me ", ".... name ",  ".... "]

    def testSplitting_noExtension(self):
        for item in self.noExtension:
            split = splitFilename(item)
            self.assertTrue(len(split[0]) != 0) # length of the filename should not be 0
            self.assertEqual(split[0], item)    # filename should be the same as the current item
            self.assertTrue(split[1] == None)   # extension should be None, as there is none present

    def testSplitting_validFilename(self):
        for item in self.validFilename:
            split = splitFilename(item)
            self.assertTrue(len(split[0]) != 0) # length of the filename should not be 0
            self.assertTrue(len(split[1]) != 0) # length of the extension should not be 0
    
    def testSplitting_invalidFilename(self):
        for item in self.invalidFilename:
            with self.assertRaises(ValueError): # the filename is invalid, should raise error
                splitFilename(item)


if __name__ == '__main__':
    unittest.main()
