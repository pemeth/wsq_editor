"""NOTICE

This algorithm is based on example MATLAB code posted by
Peter Kovesi, School of Computer Science & Software Engineering,
The University of Western Australia.
https://www.peterkovesi.com/matlabfns/FingerPrints/Docs/index.html"""

import numpy as np
import scipy.ndimage as ndimage
import scipy.signal as signal

import exceptions as e

def ridgeFreq(im, orientim, blend_sigma=8):
    """Return ridge frequencies in image `im`.
    If no 'blend_sigma' is entered, the returned frequecy image is blocky. The 'blend_sigma' specifies a gaussian
    blur sigma value for blending the neighboring frequencies into a more continuous frequency image. If specified,
    the recommended value is around or below 10.
    Inspired by matlab frequency estimation code.
    
    Parameters
    ----------
    im : numpy_array
        The input fingerprint image.
    orientim : numpy_array
        Orientation image of the fingerprint. Values need to be in radians.
    blend_sigma : int, float
        A scalar specifying the sigma of a gaussian blur. If given, the output image will result in a more continuous frequency estimation based on
        neighboring values of each pixel. Defaults to 8.
    
    Returns
    -------
        A numpy array of the same size as `im`, which contains the local papillary ridge frequencies."""
    if not isinstance(im, np.ndarray):
        raise e.InvalidDataType("The input image is not a numpy array.")
    if not isinstance(orientim, np.ndarray):
        raise e.InvalidDataType("The input orientation image is not a numpy array.")

    if im.ndim != 2:
        raise e.InvalidInputImageDimensions("The input image is not a 2D numpy array.")
    if orientim.ndim != 2:
        raise e.InvalidInputImageDimensions("The input orientation image is not a 2D numpy array.")

    if not isinstance(blend_sigma, type(None)):
        if not (isinstance(blend_sigma, int) or isinstance(blend_sigma, float)):
            raise e.InvalidDataType("The `blend_sigma` parameter is not an int or float.")

    rows, cols = im.shape
    freq = np.zeros((rows, cols))

    blocksize = 36

    for r in range(0,rows-blocksize, blocksize):
        for c in range(0,cols-blocksize, blocksize):
            orientBlk = orientim[r:r+blocksize, c:c+blocksize]
            imBlk = im[r:r+blocksize, c:c+blocksize]

            freq[r:r+blocksize, c:c+blocksize] = freqest(imBlk, orientBlk)

    if blend_sigma == None:
        return freq
    else:
        return ndimage.gaussian_filter(freq, blend_sigma)


def freqest(im, orientim, minFreq=1/25, maxFreq=1/3):
    """Frequency estimation fuction for a portion of a fingerprint image.
    The function takes an image `im` and it's corresponding orientation image `orientim` and calculates the average frequency
    of the papillary ridges in a local area. The input images should be small portions of the original fingerprint image,
    as the orientation image is averaged to get orientation in a localized area. The calculated frequencies are thresholded
    according to `minFreq` and `maxFreq`.
    
    Parameters
    ----------
    im : numpy_array
        A portion of the original fingerprint image.
    orientim : numpy_array
        A portion of the orientation image of the fingerprint. Values need to be in radians. Orientations need to correspond to `im`.
    minFreq : int, float
        Low threshold of the accepted frequencies. Defaults to 1/25.
    maxFreq : int, float
        High threshold of the accepted frequencies. Defaults to 1/3.
    
    Returns
    -------
        An array of the same size as `im` containing the local frequency of the papillary ridges."""
    rows, cols = im.shape

    # deconstruct the orientations into it's components, average them and reconstruct back into unwrapped radians
    orientim = orientim * 2
    cosorient = np.mean(np.cos(orientim))
    sinorient = np.mean(np.sin(orientim))

    orient = np.arctan2(sinorient, cosorient) / 2

    rotim = ndimage.rotate(im, orient / np.pi * 180 + 90, reshape=False) # + 90 degrees, as the section needs to be orthogonal towards the ridges

    #crop
    cropsze = np.int(np.fix(rows/np.sqrt(2)))
    offset = np.int(np.fix((rows-cropsze)/2))
    rotim = rotim[offset:offset+cropsze, offset:offset+cropsze]

    x_sig = np.sum(rotim, axis=0) # sum along the columns to get x-signature

    # find peaks and their respective distances
    peaks_idx = signal.find_peaks(x_sig)[0]
    peak_distances = np.diff(peaks_idx)
    
    # If this slice has no peaks, return a zero frequency
    if peak_distances.size == 0:
        return np.zeros((rows,cols))

    freq = 1 / np.mean(peak_distances)  # average the peak distnaces and invert to get the resulting frequency

    # threshold the frequencies
    if freq > minFreq and freq < maxFreq:
        return freq * np.ones((rows,cols))
    else:
        return np.zeros((rows,cols))
