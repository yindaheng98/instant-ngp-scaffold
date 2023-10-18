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
import sys
import math
import cv2
import glob
import re

def parse_args():
	parser = argparse.ArgumentParser(description="convert a dataset from the nsvf paper format to nerf format transforms.json")

	parser.add_argument("--aabb_scale", default=1, help="large scene scale factor")
	args = parser.parse_args()
	return args

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
	img_files = [None] * len(frame_folders)
	for frame, frame_folder in frame_folders.items():
		camera_files = {}
		for camera_file in os.listdir(os.path.join(frame_folder, 'images')):
			m = re.findall(r"^([0-9]+)", camera_file)
			if len(m) != 1:
				continue
			camera = int(m[0])
			camera_files[camera] = os.path.join(frame_folder, 'images', camera_file)
		frame_files = [None] * len(camera_files)
		for camera, camera_file in camera_files.items():
			frame_files[camera] = camera_file
		assert None not in frame_files and len(frame_files) == CAMERAS
		img_files[frame] = frame_files
	assert None not in img_files

	image = cv2.imread(img_files[0][0],cv2.IMREAD_UNCHANGED)
	w = image.shape[1]
	h = image.shape[0]

	K_lines = map(str.strip,open("pose/K.txt","r").readlines())
	T_lines = map(str.strip,open("pose/RT_c2w.txt","r").readlines())
	K_els = tuple(map(float, " ".join(K_lines).split(" ")))
	T_els = tuple(map(float, " ".join(T_lines).split(" ")))
	assert len(K_els) == 3*3*CAMERAS
	K_arrays = [np.array(K_els[i:i+3*3]).reshape((3,3)) for i in range(CAMERAS)]
	assert len(T_els) == 3*4*CAMERAS
	T_arrays = [np.array(K_els[i:i+3*4]).reshape((4,3)) for i in range(CAMERAS)]
	for K, T in zip(K_arrays, T_arrays):
		print(K)
		print(T)
