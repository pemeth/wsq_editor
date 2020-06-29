import numpy as np
from scipy.signal import convolve2d
from numpy.lib import stride_tricks
from sklearn.feature_extraction import image

def getRoi(im, blockShape=(16,16), threshold=0.1):
    """Return a region of interest mask of the input fingerprint image.
    
    Simple ROI extraction based on gray value variance inside MxN blocks.
    
    Parameters
    im:
        The input image, form which the region of interest will be extracted.
    blockShape:
        A 2-tuple specifying the block shape for which to compute the individual
        variances. Default is (16,16)
    threshold:
        A number between 0 and 1, which specifies the threshold variance for the
        region of interest. Anything over the threshold is part of the ROI.

    Returns
        A 2D numpy array of the same size as the input image containing truth values
        of each pixel being or not being in the region of interest.
    """
    patch_size = 16
    shape = (im.shape[0] - patch_size + 1, im.shape[1] - patch_size + 1, patch_size, patch_size)
    strides = 2 * im.strides
    patches = stride_tricks.as_strided(im, shape=shape, strides=strides)
    # /^\ is the equivalent of `patches = image.extract_patches_2d(im, (16,16))`
    #       but this way it's easier to reconstruct the image from the patches

    # Get the variance for each patch and normalize to 0-1 range
    var = patches.var(axis=(-1,-2))
    var = (var - np.amin(var)) * (1 / (np.amax(var) - np.amin(var)))

    # Iterate over the variance image block-wise and apply the roi mask to the block
    #  where the mean of the variance is below the threshold
    roi = np.zeros(var.shape, dtype=np.bool)
    for r in range(0, var.shape[0], patch_size):
        for c in range(0, var.shape[1], patch_size):
            v = var[r:r+patch_size, c:c+patch_size]
            if v.mean() > threshold:
                roi[r:r+patch_size, c:c+patch_size] = True # True - the block is part of a fingerprint
            else:
                roi[r:r+patch_size, c:c+patch_size] = False # False - the block is NOT part of a fingerprint

    # The patching and variance calculation reduces the image dimensions - pad it back to it's original size
    orig_height = im.shape[0]
    patched_height = var.shape[0]
    to_pad = orig_height - patched_height

    # Padding only applied to bottom and right edges, as these are the ones that were shortened
    roi = np.pad(roi, (0, to_pad), 'edge')

    return roi