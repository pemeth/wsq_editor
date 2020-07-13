import numpy as np

def bradleyThreshold(img, mask):
    """Binarizes the input image adaptively. Based on the Bradley Adaptive Thresholding method.
    
    Parameters
    ----------
    img : numpy_array
        The input image to be binarized.
    mask : numpy_array
        The binary region of interest mask of the fingerprint `img`.
        
    Returns
    -------
        A binarized version of `img`."""

    rows, cols = img.shape

    #integral image - the numpy way
    intImg = np.zeros_like(img).astype(np.int32)
    intImg = np.cumsum(np.cumsum(img, axis=0), axis=1)

    out = np.zeros_like(img).astype(np.bool)
    s = int(cols / 12) # Bradley recommends an eighth of the image width, but a twelfth seems to yield better results
    t = 15
    for i in range(cols):
        for j in range(rows):
            # check for ROI
            if not mask[j,i]:
                continue

            x1 = int(j - s/2)
            x2 = int(j + s/2)
            y1 = int(i - s/2)
            y2 = int(i + s/2)

            # border check - don't know how else to handle it
            if x1 - 1 < 0 or x2 >= rows:
                out[j,i] = False
                continue
            if y1 - 1 < 0 or y2 >= cols:
                out[j,i] = False
                continue

            count = (x2 - x1) * (y2 - y1)

            sm = intImg[x2, y2] - intImg[x2, y1 - 1] - intImg[x1 - 1, y2] + intImg[x1 - 1, y1 - 1]

            if (img [j,i] * count) <= (sm * (100 - t) / 100):
                out[j,i] = False
            else:
                out[j,i] = True
    
    return out