import numpy as np

def normalizeMeanVariance(imgArray):
    """Complex image normalization based on image mean and variance values"""
    MEAN = np.mean(imgArray)
    VAR = np.var(imgArray)

    DESIRED_VAR = 100
    DESIRED_MEAN = 100

    imgArray = np.float32(imgArray)
    imgArray = np.where(imgArray > MEAN,
                        DESIRED_MEAN + ((DESIRED_VAR * ((imgArray - MEAN)**2)) / VAR)**(1/2.0),
                        DESIRED_MEAN - ((DESIRED_VAR * ((imgArray - MEAN)**2)) / VAR)**(1/2.0))

    imMin = np.amin(imgArray)
    imMax = np.amax(imgArray)

    return np.uint8((imgArray - imMin) * (255 / (imMax - imMin)))