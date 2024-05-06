import argparse
import numpy as np
import cv2

parser = argparse.ArgumentParser()
parser.add_argument("--format", type=str, required=True, help="The path format of the saved image bin.")


def linear_to_srgb(img):
    limit = 0.0031308
    return np.where(img > limit, 1.055 * (img ** (1.0 / 2.4)) - 0.055, 12.92 * img)


if __name__ == "__main__":
    import os
    args = parser.parse_args()
    root = os.getcwd()
    data = []
    i = 0
    while os.path.isfile(args.format % i):
        binpath = args.format % i
        img = np.fromfile(binpath, dtype='float32').reshape((1080, 1920, 4))
        img = np.clip(linear_to_srgb(img[..., :3]), 0.0, 1.0)
        img_cv = cv2.cvtColor((img*255).astype(np.uint8), cv2.COLOR_BGR2RGB)
        imgpath = os.path.splitext(binpath)[0] + ".png"
        cv2.imwrite(imgpath, img_cv)
        print(binpath, imgpath)
        i += 1
