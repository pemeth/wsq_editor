import numpy as np
from PIL import Image

def normalizeMinMax(imgArray):
    """Simple image normalization based on value averaging"""
    # Image normalization (as per source: Fingerprint Authentication using Gabor Filter based Matching Algorithm)
    # Get the original shape of the image and then flatten it to a 1D array
    imgArray = imgArray.flatten()

    gMin = np.amin(imgArray)
    gMax = np.amax(imgArray)
    gRange = gMax - gMin

    # Normalize
    imgArray = (((np.float32(imgArray) - gMin) * 255) / gRange)

    return np.uint8(imgArray)

def normalizeMeanVariance(imgArray):
    """Complex image normalization based on image mean and variance values"""
    imgArray = imgArray.flatten()

    MEAN = imgArray.sum() / imgArray.size

    varSum = ((imgArray - MEAN)**2).sum()

    VAR = varSum / imgArray.size

    DESIRED_VAR = 100
    DESIRED_MEAN = 100

    imgArray = np.float32(imgArray)
    imgArray = np.where(imgArray > MEAN,
                        DESIRED_MEAN + ((DESIRED_VAR * ((imgArray - MEAN)**2)) / VAR)**(1/2.0),
                        DESIRED_MEAN - ((DESIRED_VAR * ((imgArray - MEAN)**2)) / VAR)**(1/2.0))

    return np.uint8(imgArray)