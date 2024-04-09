import argparse
import json
import bson
import numpy as np
import zlib
from scipy import sparse

parser = argparse.ArgumentParser()
parser.add_argument("--start", type=int, required=True, help="The start frame number.")
parser.add_argument("--end", type=int, required=True, help="The end frame number.")
parser.add_argument("--modelformat", type=str, required=True, help="The path format of the saved snapshot.")
parser.add_argument("--gtformat", type=str, required=True, help="The path format of the saved snapshot.")
parser.add_argument("--lrformat", type=str, required=True, help="The path format of the saved snapshot.")

if __name__ == "__main__":
    import os
    args = parser.parse_args()
    root = os.getcwd()
    for i in range(args.start, args.end + 1):
        gtpath, lrpath = args.gtformat % i, args.lrformat % i
        gt = np.fromfile(gtpath, dtype='float32').reshape((1080, 1920, 4))
        lr = np.fromfile(lrpath, dtype='float32').reshape((1080, 1920, 4))
        modelpath = args.modelformat % i
        with open(modelpath, "rb") as f:
            model = bson.decode_all(f.read())[0]
        pass
