import numpy as np
from numpy.lib import stride_tricks
from scipy.ndimage.measurements import center_of_mass

# based on https://www.researchgate.net/profile/Gabriel_Iwasokun/publication/291100504_Fingerprint_Singular_Point_Detection_Based_on_Modified_Poincare_Index_Method/links/56dd701408ae46f1e99f5649/Fingerprint-Singular-Point-Detection-Based-on-Modified-Poincare-Index-Method.pdf
def poincareIndex(window):
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

def singularityCleanup(cores, deltas):
    cores = averageSingularities(cores)

    foo, bar = np.where(cores)
    print(foo[0], bar[0])
    deltas = averageSingularities(deltas)

    cores, deltas = deleteSingularities(cores, deltas)

    return cores, deltas