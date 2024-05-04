import argparse
import os

import numpy as np
import json
import math
import cv2
import re


def parse_args():
    parser = argparse.ArgumentParser(
        description="convert a dataset from the nsvf paper format to nerf format transforms.json")

    parser.add_argument("--root", type=str, required=True, help="path to the video folder")
    parser.add_argument("--root_dst", type=str, required=True, help="path to the video folder")
    parser.add_argument("--transform", type=str, required=True, help="fmt of transforms.json")
    parser.add_argument("--start", type=int, required=True, help="The start frame number.")
    parser.add_argument("--end", type=int, required=True, help="The end frame number.")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    assert os.path.relpath(os.path.relpath(os.path.join(args.root, args.transform), args.root), args.transform) == "."
    for i in range(args.start, args.end + 1):
        transform_path = os.path.join(args.root, args.transform % i)
        transform_path_dst = os.path.join(args.root_dst, args.transform % i)
        with open(transform_path, "r", encoding="utf8") as f:
            transforms = json.load(f)
            for frame in transforms["frames"]:
                file_path = os.path.join(os.path.dirname(transform_path), frame["file_path"])
                file_path_dst = os.path.join(os.path.dirname(transform_path_dst), frame["file_path"])
                os.makedirs(os.path.dirname(file_path_dst), exist_ok=True)
                img = cv2.imread(file_path)
                grayscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                print("Writing", file_path_dst)
                cv2.imwrite(file_path_dst, grayscale)
            print("Writing", transform_path_dst)
            os.makedirs(os.path.dirname(transform_path_dst), exist_ok=True)
            with open(transform_path_dst, "w", encoding="utf8") as fp:
                json.dump(transforms, fp, indent=2)
