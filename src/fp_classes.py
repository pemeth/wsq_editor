"""Fingerprint class detection.

Author: Patrik Nemeth
Xlogin: xnemet04
School: Vysoke Uceni Technicke v Brne, Fakulta Informacnich Technologii
"""
import numpy as np

def getClass(cores, deltas):
    """Returns the class of a fingerprint based on singularity information.
    
    Parameters
    ----------
    cores : numpy_array
        A binary 2D array with non-zero values specifying the position of the cores in a fingerprint image.
    deltas : numpy_array
        A binary 2D array with non-zero values specifying the position of the deltas in a fingerprint image.
        
    Returns
    -------
        A string containing the type of the fingerprint. May return `unknown` if singularities do not match any
        of the rules."""
    numCores = np.sum(cores)
    numDeltas = np.sum(deltas)

    if numCores == 0 and numDeltas == 0:
        return "arch"
    
    if numCores == 1 and numDeltas == 1:
        return specifyLoopType(cores, deltas)

    if numCores == 2 and numDeltas == 2:
        return "whorl or twin loop"

    return "unknown"


def specifyLoopType(cores, deltas):
    """Returns the type of the fingerprint, which resembles a loop. Loop-like fingerprint classes are tented arch,
    left or light loop.
    
    Parameters
    ----------
    cores : numpy_array
        A binary 2D array with non-zero values specifying the position of the cores in a fingerprint image.
    deltas : numpy_array
        A binary 2D array with non-zero values specifying the position of the deltas in a fingerprint image.
        
    Returns
    -------
        A string containing the type of the loop."""
    cY, cX = np.where(cores)
    dY, dX = np.where(deltas)

    slope = (dY - cY) / (dX - cX)

    if slope >= 1.5:
        return "left loop"
    elif slope <= -1.5:
        return "right loop"
    else:
        return "tented arch"

