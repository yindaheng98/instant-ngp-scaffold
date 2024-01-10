#!/usr/bin/env python3

# Copyright (c) 2020-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

import argparse
import os

import numpy as np
import json
import math
import cv2
import re

def parse_args():
	parser = argparse.ArgumentParser(description="convert a dataset from the nsvf paper format to nerf format transforms.json")

	parser.add_argument("--aabb_scale", default=8, help="large scene scale factor")
	args = parser.parse_args()
	return args


# https://github.com/DarlingHang/st-nerf/blob/e0c1c32b09d90101218410443193ddabc1f66d2f/data/datasets/utils.py#L6
def campose_to_extrinsic(camposes):
    if camposes.shape[1]!=12:
        raise Exception(" wrong campose data structure!")
    
    res = np.zeros((camposes.shape[0],4,4))
    
    res[:,0,:] = camposes[:,0:4]
    res[:,1,:] = camposes[:,4:8]
    res[:,2,:] = camposes[:,8:12]
    res[:,3,3] = 1.0
    
    return res


# https://github.com/DarlingHang/st-nerf/blob/e0c1c32b09d90101218410443193ddabc1f66d2f/data/datasets/utils.py#L20
def read_intrinsics(fn_instrinsic):
    fo = open(fn_instrinsic)
    data= fo.readlines()
    i = 0
    Ks = []
    while i<len(data):
        tmp = data[i].split()
        a = [float(i) for i in tmp[0:3]]
        a = np.array(a)
        b = [float(i) for i in tmp[3:6]]
        b = np.array(b)
        c = [float(i) for i in tmp[6:9]]
        c = np.array(c)
        res = np.vstack([a,b,c])
        Ks.append(res)

        i = i+1
    Ks = np.stack(Ks)
    fo.close()

    return Ks

if __name__ == "__main__":
	args = parse_args()
	AABB_SCALE = int(args.aabb_scale)
	CAMERAS = 16
	SKIP_EARLY = 0
	VIDEO_FOLDER = "."
	frame_folders = {}
	for folder in os.listdir(VIDEO_FOLDER):
		m = re.findall(r"^frame([0-9]+)", folder)
		if len(m) != 1:
			continue
		frame = int(m[0]) - 1
		frame_folders[frame] = os.path.join(VIDEO_FOLDER, folder)
	video_files = [None] * len(frame_folders)
	for frame, frame_folder in frame_folders.items():
		camera_files = []
		for camera in range(CAMERAS):
			camera_file = os.path.join(frame_folder, 'images', f"{camera}.png")
			camera_files.append(camera_file)
		video_files[frame] = camera_files
	assert None not in video_files

	# https://github.com/DarlingHang/st-nerf/blob/e0c1c32b09d90101218410443193ddabc1f66d2f/data/datasets/frame_dataset.py#L25C23-L25C23
	camposes = np.loadtxt(os.path.join('pose', 'RT_c2w.txt'))
	Ts = campose_to_extrinsic(camposes)
	Ks = read_intrinsics(os.path.join('pose', 'K.txt'))
	# TODO: scale the sence using a smarter methods
	# TODO: c2w format LLFF/OpenGL DRB or RUB to OpenCV/Colmap RDF
	
	for frame, frame_folder in frame_folders.items():
		camera_files = video_files[frame]
		cameras_data = []
		for camera_file, K, T in zip(camera_files, Ks, Ts):
			frame_data = {
				"is_fisheye": False, # should match the sence scale
				"aabb_scale": AABB_SCALE, # should match the sence scale
			}
			img = cv2.imread(camera_file)
			w, h, _ = img.shape
			b = cv2.Laplacian(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()
			c2w = T
			# TODO: c2w format LLFF/OpenGL DRB or RUB to OpenCV/Colmap RDF
			# st-nerf c2w[[x,y,z,camera], :] to instant-ngp c2w[[x,z,y,camera], :]
			c2w[0:3,2] *= -1 # flip the y and z axis
			c2w[0:3,1] *= -1
			cameras_data.append({
				"file_path": os.path.relpath(camera_file, frame_folder),
				"transform_matrix": c2w.tolist(),
				"fl_x": K[0,0], # should match the sence scale
				"fl_y": K[1,1], # should match the sence scale
				"cx": K[0,2], # should match the sence scale
				"cy": K[1,2], # should match the sence scale
				"camera_angle_x": math.atan(w / (K[0,0] * 2)) * 2,
				"camera_angle_y": math.atan(h / (K[1,1] * 2)) * 2,
				"sharpness":b,
				"w": 1920.0, # should match the sence scale
				"h": 1080.0, # should match the sence scale
			})
		frame_data["frames"] = cameras_data
		OUT_PATH = os.path.join(frame_folder, "transforms.json")
		print(f"writing {OUT_PATH}...")
		with open(OUT_PATH, "w") as outfile:
			json.dump(frame_data, outfile, indent=2)
