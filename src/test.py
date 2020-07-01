import unittest
import numpy as np

from normalize import normalizeMeanVariance
from region_of_interest import getRoi
from ridge_orientation import ridgeOrient
from ridge_frequency import ridgeFreq
import exceptions as ex

class TestImageManipulationFunctions(unittest.TestCase):
    def setUp(self):
        # generate valid test image
        self.im = np.arange(256, dtype=np.uint8)
        self.im = np.tile(self.im, (300,1))

        # generate list of invalid datatypes
        self.invalidDTypes = [1, 1.0, "str", (1,"2"), [1, "2"]]

class TestDatatypes(TestImageManipulationFunctions):
    def test_normalization_invalid(self):
        for item in self.invalidDTypes:
            with self.assertRaises(ex.InvalidDataType):
                normalizeMeanVariance(item)
    
    def test_roi_invalid(self):
        for item in self.invalidDTypes:
            with self.assertRaises(ex.InvalidDataType):
                getRoi(item)
    
    def test_orientation_invalid(self):
        for item in self.invalidDTypes:
            with self.assertRaises(ex.InvalidDataType):
                ridgeOrient(item)

    def test_frequency_invalid(self):
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

if __name__ == '__main__':
    unittest.main()
