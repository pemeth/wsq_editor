import numpy as np
from PIL import Image

def normalize(imgArray):
    # Get the original shape of the image and then flatten it to a 1D array
    shape = imgArray.shape
    imgArray = imgArray.flatten()

    arrNew = np.empty(imgArray.size, dtype=np.uint8)

    gMin = min(imgArray)
    gMax = max(imgArray)
    gRange = gMax - gMin

    # Normalize
    for i, v in enumerate(imgArray):
        arrNew[i] = ((v - gMin) * 255) / gRange

    # Reshape to original shape of the image
    #arrNew = np.reshape(arrNew, shape)

    #imgNew = Image.fromarray(arrNew)
    #imgNew.show()
    
    return arrNew