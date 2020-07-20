"""Minutiae detection in thinned ridge images.

Author: Patrik Nemeth
Xlogin: xnemet04
School: Vysoke Uceni Technicke v Brne, Fakulta Informacnich Technologii
"""
import numpy as np

# based on http://pdfs.semanticscholar.org/f30e/64b161c26e458be8411c5559ee7a959b284f.pdf
def extractMinutiae(thinned):
    """Returns two arrays of the same size as `thinned`, which contain pixels indicating friction ridge bifurcations and
    ridge endings respectively.
    
    Parameters
    ----------
    thinned : numpy_array
        A binary array of a thinned fingerprint image.
        
    Returns
    -------
        Two binary image arrays of the same size as `thinned`. First contains the bifurcations and the second the ridge endings."""
    i, j = np.where(thinned == 1) # najdi indexy pixelov, kde su linie
    minutiae = np.zeros_like(thinned).astype(np.uint8)

    for i,j in zip(i,j):
        try:
            minutiae[i,j] += calc_minutia(thinned[i-1:i+2, j-1:j+2])
        except ValueError:
            minutiae[i,j] = 0

    bifurcations = np.where(minutiae == 6, 1, 0)
    ridgeEndings = np.where(minutiae == 2, 1, 0)
    return bifurcations, ridgeEndings

def calc_minutia(s):
    """Takes a 3x3 segment `s` and returns the number of 0->1 and 1->0 pixel crossings around the center pixel in a circular manner.
    
    Parameters
    ----------
    s : numpy_array
        A 3x3 binary array.
        
    Returns
    -------
        The number of 0->1 and 1->0 crossings between pixels around the center pixel of `s`."""
    unrolled = s[[0,0,1,2,2,2,1,0], [1,2,2,2,1,0,0,0]].astype(np.int8)    # select the "circle" around the center pixel
    diffs = np.abs(np.diff(unrolled, append=unrolled[0]))   # detect 1-0 and 0-1 pixel neighbors
    final_sum = np.sum(diffs)

    return final_sum