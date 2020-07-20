"""Fingerprint ridge thinning.

Author: Patrik Nemeth
Xlogin: xnemet04
School: Vysoke Uceni Technicke v Brne, Fakulta Informacnich Technologii
"""
import numpy as np

def neighborCount(window):
    """Find the number of neighboring 1 pixels around the center pixel in a 3x3 window `window`.
    
    Parameters
    ----------
    window : numpy_array
        A 3x3 window centered around a pixel for which to count neighbors.

    Returns
    -------
        The number of neighbors around the center pixel."""
    counter = np.ones((3,3))
    counter[1,1] = 0

    return np.sum(window * counter)

def zeroToOnePatternCount(unrolled_window):
    """Find the number of 0 to 1 transitions in the cyclic array `unrolled_window`.
    
    Parameters
    ----------
    unrolled_window : numpy_array
        A 1D numpy array of binary values found in a 3x3 window around a center pixel unrolled
        in a circular fashion. This window is made cyclic for the calculations.
        Ex.:
            if the 3x3 window looks like this:  0 1 2
                                                3 4 5
                                                6 7 8,
            then the unrolled window is the values: 0,1,2,5,8,7,6,3. Internally a ninth value is added,
            so the window is cyclic - this value would in this case be 0.

    Returns
    -------
        The number of 0->1 patterns in the binary `unrolled_window`."""
    # check where values change from 1 to 0 and from 0 to 1
    #   diff outputs -1 where 1->0 and 1 where 0->1
    diffs = np.diff(unrolled_window, append=unrolled_window[0])

    # we care about the 0->1, therefore the 1's
    #   summing these values gives us the number of 0->1 patterns
    return diffs[diffs == 1].sum()

def zhangSuen(im):
    """Binary image thinning based on the Zhang-Suen method.
    
    Parameters
    ----------
    im : numpy_array
        The input binary image to be thinned.
        
    Returns
    -------
        Thinned image of the same size as `im`."""
    # indices for the unrolled window corresponding to the pixels specified in the Zhang-Suen paper
    P2, P3, P4, P5, P6, P7, P8, P9 = 0,1,2,3,4,5,6,7

    foo = np.zeros_like(im)
    foo[1:-1,1:-1] = 1

    im = foo * im

    im_cp = np.copy(im)

    still_going1, still_going2 = True, True
    while still_going1 or still_going2:
        still_going1, still_going2 = False, False
        
        i,j = np.where(im)
        for i, j in zip(i, j):
            window = im[i-1:i+2, j-1:j+2]   # take a 3x3 window around the current pixel
            unrolled = window[[0,0,1,2,2,2,1,0], [1,2,2,2,1,0,0,0]]    # select the "circle" around the center pixel

            if  (2 <= neighborCount(window) <= 6 and
                zeroToOnePatternCount(unrolled) == 1 and
                unrolled[P2] * unrolled[P4] * unrolled[P6] == 0 and
                unrolled[P4] * unrolled[P6] * unrolled[P8] == 0):
                im_cp[i,j] = 0
                still_going1 = True
        
        im = np.copy(im_cp)
        i,j = np.where(im)
        for i, j in zip(i, j):
            # same as the first subiteration, with the deletion conditions changed as per Zhang-Suen
            window = im[i-1:i+2, j-1:j+2]
            unrolled = window[[0,0,1,2,2,2,1,0], [1,2,2,2,1,0,0,0]]

            if  (2 <= neighborCount(window) <= 6 and
                zeroToOnePatternCount(unrolled) == 1 and
                unrolled[P2] * unrolled[P4] * unrolled[P8] == 0 and
                unrolled[P2] * unrolled[P6] * unrolled[P8] == 0):
                im_cp[i,j] = 0
                still_going2 = True

        im = np.copy(im_cp)

    return im
