import numpy as np

def normalizeMeanVariance(im):
    """Image normalization based on desired image mean and variance (both 100) values.
    
    Parameters
    ----------
    im : numpy_array
        The input grayscale image to be normalized.
        
    Returns
    -------
        Normalised image of the same size as `im`."""
    MEAN = np.mean(im)
    VAR = np.var(im)

    DESIRED_VAR = 100
    DESIRED_MEAN = 100

    im = np.float32(im)
    im = np.where(im > MEAN,
                        DESIRED_MEAN + ((DESIRED_VAR * ((im - MEAN)**2)) / VAR)**(1/2.0),
                        DESIRED_MEAN - ((DESIRED_VAR * ((im - MEAN)**2)) / VAR)**(1/2.0))

    imMin = np.amin(im)
    imMax = np.amax(im)

    return np.uint8((im - imMin) * (255 / (imMax - imMin)))