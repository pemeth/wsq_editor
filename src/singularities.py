"""Singularity detection via Poincare index.

Author: Patrik Nemeth
Xlogin: xnemet04
School: Vysoke Uceni Technicke v Brne, Fakulta Informacnich Technologii
"""
import numpy as np
from numpy.lib import stride_tricks
from scipy.ndimage.measurements import center_of_mass

def poincareIndex(window):
    """Calculate the poincare index of the center pixel in `window`.

    Parameters
    ----------
    window : numpy_array
        A 3x3 window with the center pixel being the one for which to calculate the index.

    Returns
    -------
        The Poincare index."""
    unrolled_cyclic = window[[2,2,1,0,0,0,1,2,2],[1,0,0,0,1,2,2,2,1]]  # select the "circle" around the center pixel, but the last item == first item

    # get all the pairs of the unrolled cyclic window
    size = 2
    shape = (unrolled_cyclic.shape[0] - size + 1, size)
    strides = unrolled_cyclic.strides * 2
    pairs = stride_tricks.as_strided(unrolled_cyclic, shape=shape, strides=strides)

    diffs = np.diff(pairs, axis=1).reshape((8,))    # calculate the differences between pairs

    betas = np.zeros(8)
    betas = np.where(diffs <= -np.pi/2, diffs+np.pi, diffs - np.pi)
    betas = np.where((diffs > -np.pi/2) & (diffs <= np.pi/2), diffs, diffs - np.pi)

    return (1 / np.pi) * np.sum(betas)  # return the poincare index of this window

def poincare(img):
    """Find cores and deltas in the fingerprint image based on the Poincare index.
    Based on:
    Iwasokun, G. a Akinyokun, O. Fingerprint Singular Point Detection Based on
    Modified Poincare Index Method. International Journal of Signal Processing, Image
    Processing and Pattern Recognition. Oktober 2014, roc. 7, s. 259–272.

    Parameters
    ----------
    img : numpy_array
        A 2D array representing the orientations of the ridges at every pixel.

    Returns
    -------
        Two binary 2D arrays of the same size as `img` with non-zero values where based on the Poincare index
        cores or deltas were found. The first returned array represents the cores and the second the deltas."""
    # TODO try to calculate the poincare indices via these patches - may be faster than a nested loop
    size = 3
    shape = (img.shape[0] - size + 1, img.shape[1] - size + 1, size, size)
    strides = 2 * img.strides
    patches = stride_tricks.as_strided(img, shape=shape, strides=strides)

    Pcs = np.zeros_like(img).astype(np.float32)
    deltas = np.zeros_like(img).astype(np.float32)
    cores = np.zeros_like(img).astype(np.float32)
    for i in range(1, img.shape[0] - 1):
        for j in range(1, img.shape[1] - 1):
            window = img[i-1:i+2, j-1:j+2]   # take a 3x3 window around the current pixel
            Pc = poincareIndex(window)
            Pcs[i,j] = Pc
            if Pc >= -1 and Pc <= -0.5:
                cores[i,j] = 1
            if Pc >= 0.5 and Pc <= 1:
                deltas[i,j] = 1

    return (cores, deltas)

def averageSingularities(sings, regionSize=8):
    """Reduce the number of singularities in `sings` in region of size `regionSize`. If multiple singularities
    are found in a region, take the average position of the singularities and replace them with this one average
    singularity.

    Parameters
    ----------
    sings : numpy_array
        A 2D binary array with nonzero values in fields where singularities were found. This variable has to contain
        only one type of singularity - either only cores or only deltas.
    regionSize : int
        The size of the region around each found singularity, from which the average will be computed.
        Defaults to 8.

    Returns
    -------
        A binary 2D array of the same size as `sings`, but with averaged positions of the singularities."""
    left = right = up = down = regionSize
    shape = sings.shape

    rows, cols = np.where(sings)
    for i, j in zip(rows,cols):
        # if near borders, set the regions, so that they do not reach out of bounds
        if i - left < 0:
            left = i
        elif i + right >= shape[0]:
            right = shape[0] - i + 1
            
        if j - up < 0:
            up = j
        elif j + down >= shape[1]:
            down = shape[1] - j + 1

        coreRegion = sings[i-left : i+right, j-up : j+down]

        coreSum = np.sum(coreRegion)

        if coreSum > 1:
            y, x = center_of_mass(coreRegion)
            coreRegion[:,:] = 0
            coreRegion[int(y), int(x)] = 1
            sings[i-left : i+right, j-up : j+down] = coreRegion

        left = right = up = down = regionSize
    
    return sings

def deleteSingularities(cores, deltas, regionSize=8):
    """Delete singularities of both types if within the same region of size `regionSize`.
    The size of both `cores` and `deltas` must match.

    Parameters
    ----------
    cores : numpy_array
        A 2D binary array with nonzero values in fields where cores were found.
    deltas : numpy_array
        A 2D binary array with nonzero values in fields where deltas were found.
    regionSize : int
        The size of the region around each found singularity, in which the singularities will be deleted.
        Defaults to 8.

    Returns
    -------
        Returns `cores` and `deltas` in this order, only with non-zero values zeroed out where markers for
        their respective singularities were found in the same region."""
    left = right = up = down = regionSize
    shape = cores.shape

    rows, cols = np.where(cores)

    for i, j in zip(rows, cols):
        # if near borders, set the regions, so that they do not reach out of bounds
        if i - left < 0:
            left = i
        elif i + right >= shape[0]:
            right = shape[0] - i + 1
            
        if j - up < 0:
            up = j
        elif j + down >= shape[1]:
            down = shape[1] - j + 1

        coreRegion = cores[i-left : i+right, j-up : j+down]
        deltaRegion = deltas[i-left : i+right, j-up : j+down]

        if np.sum(coreRegion) >= 1 and np.sum(deltaRegion) >= 1:
            cores[i-left : i+right, j-up : j+down] = 0
            deltas[i-left : i+right, j-up : j+down] = 0

        left = right = up = down = regionSize

    return cores, deltas

def deleteNearMask(sings, mask, regionSize=8):
    """Delete singularities near the edge of a region of interest mask.

    Parameters
    ----------
    sings : numpy_array
        A 2D binary array with nonzero values in fields where singularities were found. This variable has to contain
        only one type of singularity - either only cores or only deltas.
    mask : numpy_array
        A 2D binary array with nonzero values denoting the region of interest.
    regionSize : int
        The size of the region around each found singularity, in which the singularities will be deleted.
        Defaults to 8.

    Returns
    -------
        A binary 2D array of the same size as `sings`, but with deleted singularities near the ROI `mask`."""
    left = right = up = down = regionSize
    rows, cols = np.nonzero(sings)

    mask = np.invert(mask.astype(np.bool))

    shape = sings.shape

    for i, j in zip(rows, cols):
        # if near borders, set the regions, so that they do not reach out of bounds
        if i - left < 0:
            left = i
        elif i + right >= shape[0]:
            right = shape[0] - i + 1
            
        if j - up < 0:
            up = j
        elif j + down >= shape[1]:
            down = shape[1] - j + 1

        # if near mask, remove singularity
        if np.sum(mask[i-left : i+right, j-up : j+down]) != 0:
            sings[i,j] = 0

    return sings

def singularityCleanup(cores, deltas, mask=None):
    """Calls `averageSingularities` and `deleteSingularities` in this order in order to clean up
    the singularity images.
    Based on:
    Iwasokun, G. a Akinyokun, O. Fingerprint Singular Point Detection Based on
    Modified Poincare Index Method. International Journal of Signal Processing, Image
    Processing and Pattern Recognition. Oktober 2014, roc. 7, s. 259–272.

    Parameters
    ----------
    cores : numpy_array
        A 2D binary array with nonzero values in fields where cores were found.
    deltas : numpy_array
        A 2D binary array with nonzero values in fields where deltas were found.
    mask : numpy_array
        A 2D binary array with nonzero values denoting the region of interest.

    Returns
    -------
        The cleaned versions of `cores` and `deltas` in this order."""
    cores = averageSingularities(cores)
    deltas = averageSingularities(deltas)

    cores, deltas = deleteSingularities(cores, deltas)

    if not isinstance(mask, type(None)):
        cores = deleteNearMask(cores, mask)
        deltas = deleteNearMask(deltas, mask)

    return cores, deltas