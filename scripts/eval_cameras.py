import argparse
import json
import bson
import numpy as np
import zlib
import cv2
from scipy import sparse
from common import linear_to_srgb

parser = argparse.ArgumentParser()
parser.add_argument("--start", type=int, required=True, help="The start frame number.")
parser.add_argument("--end", type=int, required=True, help="The end frame number.")
parser.add_argument("--modelformat", type=str, required=True, help="The path format of the saved snapshot.")
parser.add_argument("--gtformat", type=str, required=True, help="The path format of the saved snapshot.")
parser.add_argument("--lrformat", type=str, required=True, help="The path format of the saved snapshot.")
parser.add_argument("--save", type=str, required=True, help="The path format of the saved snapshot.")

def get_size(data):
    data_compressed = zlib.compress(data.tobytes())
    data_csr = sparse.csr_matrix(data)
    data_csr_compressed = zlib.compress(data_csr.data.tobytes())
    return min(len(data_compressed), len(data_csr_compressed))

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
    data = []
    video_gt = cv2.VideoWriter(args.save + '.gt.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 10, (1920,1080))
    video_lr = cv2.VideoWriter(args.save + '.lr.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 10, (1920,1080))
    for i in range(args.start, args.end + 1):
        gtpath, lrpath = args.gtformat % i, args.lrformat % i
        try:
            gt = np.fromfile(gtpath, dtype='float32').reshape((1080, 1920, 4))
            lr = np.fromfile(lrpath, dtype='float32').reshape((1080, 1920, 4))
            gt = np.clip(linear_to_srgb(gt[...,:3]), 0.0, 1.0)
            lr = np.clip(linear_to_srgb(lr[...,:3]), 0.0, 1.0)
            modelpath = args.modelformat % i
            with open(modelpath, "rb") as f:
                model = bson.decode_all(f.read())[0]
            intra, inter = np.frombuffer(model["intra"], dtype=np.float16), np.frombuffer(model["inter"], dtype=np.float16)
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
            del model['density_grid']
            del model['density_grid_bitfield']
            del model['inter']
            del model['intra']
            del model['params']
            model['intra_size'] = intra_zlib
            model['inter_size'] = inter_zlib
            model['psnr'] = psnr
            data.append(model)
            gt_cv = cv2.cvtColor((gt*255).astype(np.uint8), cv2.COLOR_BGR2RGB)
            lr_cv = cv2.cvtColor((lr*255).astype(np.uint8), cv2.COLOR_BGR2RGB)
            video_gt.write(gt_cv)
            video_lr.write(lr_cv)
        except Exception as e:
            print(e)
    with open(args.save, "w", encoding="utf8") as f:
        json.dump(data, f, indent=2)
