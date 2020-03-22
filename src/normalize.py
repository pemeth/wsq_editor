import numpy as np
from PIL import Image

def normalizeMinMax(imgArray):
    # Image normalization (as per source: Fingerprint Authentication using Gabor Filter based Matching Algorithm)
    # Get the original shape of the image and then flatten it to a 1D array
    imgArray = imgArray.flatten()

    gMin = min(imgArray)
    gMax = max(imgArray)
    gRange = gMax - gMin

    # Normalize
    for i, v in enumerate(imgArray):
        imgArray[i] = ((v - gMin) * 255) / gRange
    
    return imgArray

def normalizeMeanVariance(imgArray):
    imgArray = imgArray.flatten()

    MEAN = imgArray.sum() / imgArray.size

    varSum = 0
    for i in imgArray:
        varSum = varSum + (i - MEAN) ** 2

    VAR = varSum / imgArray.size

    DESIRED_VAR = 100
    DESIRED_MEAN = 100

    for i, _ in enumerate(imgArray):
        if imgArray[i] > MEAN:
            imgArray[i] = DESIRED_MEAN + ((DESIRED_VAR * ((imgArray[i] - MEAN)**2)) / VAR)**(1/2.0)
        else:
            imgArray[i] = DESIRED_MEAN - ((DESIRED_VAR * ((imgArray[i] - MEAN)**2)) / VAR)**(1/2.0)

    return imgArray