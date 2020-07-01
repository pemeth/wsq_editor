import numpy as np
from scipy.signal import convolve2d
from scipy.ndimage import gaussian_filter

BLOCK_HEIGHT = 16
BLOCK_WIDTH = 16

def ridgeOrient(im, flip=False):
    """Takes a normalized fingerprint image array and returns an orientation image of the same size."""

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
    phiX = gaussian_filter(phiX, 3)
    phiY = gaussian_filter(phiY, 3)

    # Convert the vector field into an orientation image
    orientation = np.pi / 2 + np.arctan2(phiY, phiX) / 2

    return orientation
