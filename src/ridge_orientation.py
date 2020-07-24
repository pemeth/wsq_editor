"""Ridge orientation estimation.

Author: Patrik Nemeth
Xlogin: xnemet04
School: Vysoke Uceni Technicke v Brne, Fakulta Informacnich Technologii
"""
import numpy as np
from scipy.signal import convolve2d
from scipy.ndimage import gaussian_filter

import exceptions as e

BLOCK_HEIGHT = 16
BLOCK_WIDTH = 16

def ridgeOrient(im, flip=False):
    """Takes a normalized fingerprint image array and returns an orientation image of the same size.
    Based on:
    Hong, L., Wan, Y. a Jain, A. Fingerprint image enhancement: algorithm and
    performance evaluation. IEEE Transactions on Pattern Analysis and Machine
    Intelligence. IEEE. 1998, roc. 20, c. 8, s. 777–789. ISSN 0162-8828.
    
    Parameters
    ----------
    im : numpy_array
        The input fingerprint image.
    flip : bool
        A hack for plotting a vector field based on the output image. See comment in the code for further info.
        Defaults to False.
        
    Returns
    -------
        A 2D array of the same size as `im` with fields containing values from 0 to Pi (~3.14) specifying the
        angle of the ridges in the image."""
    if not isinstance(im, np.ndarray):
        raise e.InvalidDataType("The input image is not a numpy array.")

    if im.ndim != 2:
        raise e.InvalidInputImageDimensions("The input image is not a 2D numpy array.")

    if not isinstance(flip, bool):
        raise e.InvalidDataType("The `flip` optional parameter needs to be a boolean.")

    if flip:
        # This is a hack for correctly showing the orientation vector field via pyplot's quiver. If this isn't flipped,
        #   the vector field is mirrored. After flipping the computed orientation image, the vector field breaks.
        #   This could probably be fixed with some mathematical magic, but I have no idea how, so I'm "pre-flipping" at this stage,
        #   which fixes the issue.
        im = np.flip(im,1)

    # Compute gradients along the X and Y axes
    dY, dX = np.gradient(im)

    # Pre-compute the terms of summation
    dXY = dX*dY * 2
    dXX = dX**2
    dYY = dY**2

    # Create a "ones" matrix and sum the terms using convolution
    sumMatrix = np.ones((BLOCK_HEIGHT, BLOCK_WIDTH))
    vX = convolve2d(dXY, sumMatrix, mode='same')
    vY = convolve2d(dXX - dYY, sumMatrix, mode='same')

    theta = np.arctan2(vX, vY) / 2

    phiX = np.cos(2 * theta)
    phiY = np.sin(2 * theta)

    # Smoothe the vector field
    phiX = gaussian_filter(phiX, 14)
    phiY = gaussian_filter(phiY, 14)

    # Convert the vector field into an orientation image
    orientation = np.pi / 2 + np.arctan2(phiY, phiX) / 2

    return orientation
