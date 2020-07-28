import numpy as np
from normalize import normalizeMeanVariance
from region_of_interest import getRoi
from ridge_orientation import ridgeOrient
from filters import butterworth
from singularities import poincare, singularityCleanup
from fp_classes import getClass

import os
import argparse
from glob import glob
from PIL import Image

def checkClasses(file_path, expect):
    files = {}

    if file_path[-1] == '/':
        file_path = file_path[:-1]

    if os.path.isdir(file_path):
        files = glob(file_path + "/*.bmp")
    elif os.path.isfile(file_path):
        files = [file_path]
    else:
        print("Special files not supported.")
        return

    countAll = len(files)
    countCorrect = 0

    with open(file_path + "/out.txt", mode="w") as out:
        out.write("FILE : CLASS" + "\r\n")
        print("FILE : CLASS ; core count | delta count")
        for f in files:
            img = Image.open(f)
            img = img.convert("L")
            img = np.asarray(img)

            norm = normalizeMeanVariance(img)
            butter = butterworth(norm)
            mask = getRoi(butter)
            orient = ridgeOrient(butter * mask, blendSigma=14)
            cores, deltas = poincare(orient) * mask
            cores, deltas = singularityCleanup(cores, deltas, mask)

            fpClass = getClass(cores, deltas)

            out.write(f + " : " + fpClass + "\r\n")
            print(f + " : " + fpClass, " ; ", np.sum(cores), " | ", np.sum(deltas))
            if expect == fpClass:
                countCorrect += 1

        errorRate = ((countAll - countCorrect) * 100) / countAll
        print("Number of tested files: ", str(countAll))
        print("Number of correct classifications: ", str(countCorrect))
        print("Error rate: " + str(errorRate))

        out.write("Number of tested files: " + str(countAll))
        out.write("Number of correct classifications: " + str(countCorrect))
        out.write("Error rate: " + str(errorRate))

def main():
    parser = argparse.ArgumentParser("Testing framework.")

    parser.add_argument('directory', action='store', type=str, metavar='DIR',
                        help='Do fingerprint class evaluation on fingerprints stored in directory DIR. DIR is a'
                                'path to a directory containing images in bitmap format (.bmp).')

    parser.add_argument('expected', action='store', type=str, metavar='expected',
                        choices=['arch', 'tented arch', 'left loop', 'right loop', 'whorl or twin loop'],
                        help='One of the following: arch, tented arch, left loop, right loop, whorl or twin loop.'
                                'Specifies what class the evaluator should expect in DIR. The ones with multiple words'
                                'need to be in quotes.')

    args = parser.parse_args()
    
    checkClasses(args.directory, args.expected)

if __name__ == "__main__":
    main()
