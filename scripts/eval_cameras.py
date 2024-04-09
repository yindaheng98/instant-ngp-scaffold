import argparse
import json
import bson
import numpy as np
import zlib
from scipy import sparse
from common import linear_to_srgb

parser = argparse.ArgumentParser()
parser.add_argument("--start", type=int, required=True, help="The start frame number.")
parser.add_argument("--end", type=int, required=True, help="The end frame number.")
parser.add_argument("--modelformat", type=str, required=True, help="The path format of the saved snapshot.")
parser.add_argument("--gtformat", type=str, required=True, help="The path format of the saved snapshot.")
parser.add_argument("--lrformat", type=str, required=True, help="The path format of the saved snapshot.")

def get_size(data):
    data_compressed = zlib.compress(data)
    return len(data_compressed)

def calculate_psnr(img1, img2, max_value=255):
    """"Calculating peak signal-to-noise ratio (PSNR) between two images."""
    mse = np.mean((np.array(img1, dtype=np.float32) - np.array(img2, dtype=np.float32)) ** 2)
    if mse == 0:
        return 100
    return 20 * np.log10(max_value / (np.sqrt(mse)))

if __name__ == "__main__":
    import os
    import matplotlib.pyplot as plt
    args = parser.parse_args()
    root = os.getcwd()
    for i in range(args.start, args.end + 1):
        gtpath, lrpath = args.gtformat % i, args.lrformat % i
        gt = np.fromfile(gtpath, dtype='float32').reshape((1080, 1920, 4))
        lr = np.fromfile(lrpath, dtype='float32').reshape((1080, 1920, 4))
        gt = np.clip(linear_to_srgb(gt[...,:3]), 0.0, 1.0)
        lr = np.clip(linear_to_srgb(lr[...,:3]), 0.0, 1.0)
        modelpath = args.modelformat % i
        with open(modelpath, "rb") as f:
            model = bson.decode_all(f.read())[0]
        intra, inter = model["intra"], model["inter"]
        intra_zlib = get_size(intra)
        inter_zlib = get_size(inter)
        psnr = calculate_psnr(lr, gt, max_value=1)
        print(intra_zlib, inter_zlib, psnr)
        # fig = plt.figure(figsize=(6, 3))
        # ax = fig.subplots(nrows=1, ncols=2)
        # ax[0].imshow(gt)
        # ax[1].imshow(lr)
        # plt.show()
        # plt.close(fig)
        pass
