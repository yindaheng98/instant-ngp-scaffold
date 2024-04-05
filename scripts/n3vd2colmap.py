#!/usr/bin/env python3

# Copyright (c) 2020-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

import argparse
from copy import deepcopy
import os
import cv2

import numpy as np
import json
import math
import re
import tempfile
import shutil

def parse_args():
	parser = argparse.ArgumentParser(description="convert a dataset from the nsvf paper format to nerf format transforms.json")

	parser.add_argument("--aabb_scale", default=8, help="large scene scale factor")
	parser.add_argument("--path", type=str, required=True, help="path to the video folder")
	parser.add_argument("--run_colmap", action="store_true")
	parser.add_argument("--residual_thr", type=float, default=4, help="residual threshold")
	parser.add_argument("--mask_density_x", type=int, default=4)
	parser.add_argument("--mask_density_y", type=int, default=4)
	parser.add_argument("--fmt", type=str, default=r"^cam([0-9]+)$", help="re format of image folder")
	args = parser.parse_args()
	return args

if __name__ == "__main__":
	import sys
	args = parse_args()
	AABB_SCALE = int(args.aabb_scale)
	FRAMES = 300
	root = os.path.abspath(os.path.dirname(sys.argv[0]))
	args = parse_args()
	VIDEO_FOLDER = args.path
	tempdir = os.path.join(VIDEO_FOLDER, "colmap")
	imgfolder = os.path.join(tempdir, "images")
	os.makedirs(imgfolder, exist_ok=True)
	camera_folders = []
	for folder in os.listdir(VIDEO_FOLDER):
		m = re.search(args.fmt, folder)
		if not m:
			continue
		name = m.group()
		camera_folders.append(os.path.join(VIDEO_FOLDER, folder))
		camera_file = os.path.join(VIDEO_FOLDER, folder, "001.png")
		temp_file = os.path.join(imgfolder, name + ".png")
		shutil.copyfile(camera_file, temp_file)
		script = os.path.join(root, "colmap2nerf.py")
	if args.run_colmap:
		cmd = f"cd {tempdir} && python {script} --images ./images --run_colmap --aabb_scale {args.aabb_scale} --overwrite"
		os.system(cmd)
	camera_folders = []
	for folder in os.listdir(VIDEO_FOLDER):
		m = re.findall(args.fmt, folder)
		if len(m) != 1:
			continue
		camera_folder = os.path.join(VIDEO_FOLDER, folder)
		camera_folders.append(camera_folder)
		FRAMES = min(FRAMES, len(os.listdir(camera_folder)))
	camera_folders = sorted(camera_folders)
	video_files = [[] for _ in range(FRAMES)]
	for frame in range(FRAMES):
		for camera_folder in camera_folders:
			frame_file = os.path.join(camera_folder, "%03d.png" % (frame + 1))
			video_files[frame].append(frame_file)
	transforms_file = os.path.join(tempdir, "transforms.json")
	with open(transforms_file) as f:
		data = json.load(f)
	last_frames = {}
	for frame, camera_files in enumerate(video_files):
		frame_folder = os.path.join(VIDEO_FOLDER, "frame%d" % (frame + 1))
		cameras = deepcopy(data)
		for camera in cameras["frames"]:
			camera_name = os.path.splitext(os.path.basename(camera["file_path"]))[0]
			camera_file = os.path.join("..", camera_name, "%03d.png" % (frame + 1))
			camera["file_path"] = camera_file
		os.makedirs(frame_folder, exist_ok=True)
		print("writing", frame_folder)
		with open(os.path.join(frame_folder, "transforms.json"), "w", encoding="utf8") as f:
			json.dump(cameras, f, indent=2)
		if frame > 0:
			residual_folder = os.path.join(VIDEO_FOLDER, "residuals", "frame%d" % (frame + 1))
			os.makedirs(residual_folder, exist_ok=True)
			for camera in cameras["frames"]:
				camera_name = os.path.basename(os.path.dirname(camera["file_path"]))
				camera_file = os.path.join("..", camera["file_path"])
				residual_file = os.path.join(".", "%s.png" % camera_name)
				camera["file_path"] = camera_file
				camera["mask_path"] = residual_file
				img = cv2.imread(os.path.join(VIDEO_FOLDER, camera_name, "%03d.png" % (frame + 1)))
				residual = cv2.absdiff(last_frames[camera_name], img)
				idx = (residual >= args.residual_thr).any(axis=2)
				residual = residual.sum(axis=2)
				residual[idx] = 0
				residual[~idx] = 255
				residual[0::args.mask_density_x, 0::args.mask_density_y] = 0
				cv2.imwrite(os.path.join(residual_folder, residual_file), residual.astype(np.uint8))
				last_frames[camera_name] = img
			with open(os.path.join(residual_folder, "transforms.json"), "w", encoding="utf8") as f:
				json.dump(cameras, f, indent=2)
		else:
			for camera in cameras["frames"]:
				camera_name = os.path.basename(os.path.dirname(camera["file_path"]))
				last_frames[camera_name] = cv2.imread(os.path.join(VIDEO_FOLDER, camera_name, "%03d.png" % (frame + 1)))
			
		
	