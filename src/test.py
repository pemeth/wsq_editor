import unittest
import numpy as np

from normalize import normalizeMeanVariance
from region_of_interest import getRoi
from ridge_orientation import ridgeOrient
from ridge_frequency import ridgeFreq
from filters import gaborFilter
import exceptions as ex

class TestImageManipulationFunctions(unittest.TestCase):
    def setUp(self):
        # generate valid test image
        self.im = np.arange(256, dtype=np.uint8)
        self.im = np.tile(self.im, (300,1))

        # generate list of invalid datatypes
        self.invalidDTypes = [1, 1.0, "str", (1,"2"), [1, "2"]]

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
                

if __name__ == '__main__':
    unittest.main()
