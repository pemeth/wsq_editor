import numpy as np

def getClass(cores, deltas):
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
    cY, cX = np.where(cores)
    dY, dX = np.where(deltas)

    slope = (dY - cY) / (dX - cX)

    if slope >= 1.5:
        return "left loop"
    elif slope <= -1.5:
        return "right loop"
    else:
        return "tented arch"

