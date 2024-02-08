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
	parser.add_argument("--path", type=str, required=True, help="path to the video folder")
	parser.add_argument("--scale", type=float, required=True, help="scale after aabb_scale")
	parser.add_argument("--shift0", type=float, default=0., help="shift before aabb_scale")
	parser.add_argument("--shift1", type=float, default=0., help="shift before aabb_scale")
	parser.add_argument("--shift2", type=float, default=0., help="shift before aabb_scale")
	parser.add_argument("--residual_root", type=str, required=True, help="root path to the residual images")
	parser.add_argument("--residual_transform_test", action="store_true")
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
	VIDEO_FOLDER = args.path
	RESIDUAL_FOLDER = args.residual_root
	frame_folders = {}
	frame_residual_folders = {}
	for folder in os.listdir(VIDEO_FOLDER):
		m = re.findall(r"^frame([0-9]+)", folder)
		if len(m) != 1:
			continue
		frame = int(m[0]) - 1
		frame_folders[frame] = os.path.join(VIDEO_FOLDER, folder)
		frame_residual_folders[frame] = os.path.join(RESIDUAL_FOLDER, folder)
	video_files = {}
	video_residual_files = {}
	frame_idx = []
	for frame, frame_folder in frame_folders.items():
		camera_files = []
		camera_residual_files = []
		for camera in range(CAMERAS):
			camera_file = os.path.join(frame_folder, 'images', f"{camera}.png")
			camera_files.append(camera_file)
			camera_residual_file = os.path.join(frame_residual_folders[frame], f"{camera}.png")
			camera_residual_files.append(camera_residual_file)
		video_files[frame] = camera_files
		video_residual_files[frame] = camera_residual_files
		frame_idx.append(frame)
	frame_idx = sorted(frame_idx)

	# https://github.com/DarlingHang/st-nerf/blob/e0c1c32b09d90101218410443193ddabc1f66d2f/data/datasets/frame_dataset.py#L25C23-L25C23
	camposes = np.loadtxt(os.path.join(VIDEO_FOLDER, 'pose', 'RT_c2w.txt'))
	Ts = campose_to_extrinsic(camposes)
	Ks = read_intrinsics(os.path.join(VIDEO_FOLDER, 'pose', 'K.txt'))
	# TODO: scale the sence using a smarter methods
	# TODO: c2w format LLFF/OpenGL DRB or RUB to OpenCV/Colmap RDF
	stnerf = Ts[:, :3, :]
	pos = stnerf[:, :, 3]
	pos = pos - pos.mean(axis=0)
	scale = (pos.max(axis=0) - pos.min(axis=0)).max()
	pos = pos / scale * 2
	pos[:, 0] += args.shift0
	pos[:, 1] += args.shift1
	pos[:, 2] += args.shift2
	pos = pos * AABB_SCALE * args.scale
	stnerf[:, :, 3] = pos
	Ts[:, :3, :] = stnerf
	Ts[:, 0:3, 2] *= -1 # flip the y and z axis
	Ts[:, 0:3, 1] *= -1
	Ts = Ts[:, [2,1,0,3], :]
	Ts[:, 2, :] *= -1 # flip whole world upside down
	
	all_frame_data = {
		"is_fisheye": False, # should match the sence scale
		"aabb_scale": AABB_SCALE, # should match the sence scale
		"frames": []
	}
	last_frames = {}
	for frame in frame_idx:
		frame_folder = frame_folders[frame]
		camera_files = video_files[frame]
		camera_residual_files = video_residual_files[frame]
		cameras_data = []
		for cam_i, (camera_file, K, c2w, camera_residual_file) in enumerate(zip(camera_files, Ks, Ts, camera_residual_files)):
			frame_data = {
				"is_fisheye": False, # should match the sence scale
				"aabb_scale": AABB_SCALE, # should match the sence scale
			}
			img = cv2.imread(camera_file)
			h, w, _ = img.shape
			b = cv2.Laplacian(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()
			camera_data = {
				"transform_matrix": c2w.tolist(),
				"fl_x": K[0,0], # should match the sence scale
				"fl_y": K[1,1], # should match the sence scale
				"cx": K[0,2], # should match the sence scale
				"cy": K[1,2], # should match the sence scale
				"camera_angle_x": math.atan(w / (K[0,0] * 2)) * 2,
				"camera_angle_y": math.atan(h / (K[1,1] * 2)) * 2,
				"sharpness":b,
				"w": w, # should match the sence scale
				"h": h, # should match the sence scale
				"file_path": os.path.relpath(camera_file, frame_folder),
			}
			if cam_i in last_frames:
				os.makedirs(os.path.dirname(camera_residual_file), exist_ok=True)
				residual = cv2.subtract(last_frames[cam_i], img)
				cv2.imwrite(camera_residual_file, residual)
				camera_data["residual_path"] = os.path.relpath(camera_residual_file, frame_folder)
			last_frames[cam_i] = img
			cameras_data.append(camera_data)
			all_frame_data["frames"].append({
				**camera_data,
				"file_path": camera_file,
				"residual_path": camera_residual_file
			})
		frame_data["frames"] = cameras_data
		OUT_PATH = os.path.join(frame_folder, "transforms.json")
		print(f"writing {OUT_PATH}...")
		with open(OUT_PATH, "w") as outfile:
			json.dump(frame_data, outfile, indent=2)
		if args.residual_transform_test:
			frame_residual_folder = frame_residual_folders[frame]
			for camera_data in frame_data["frames"]:
				if "residual_path" not in camera_data:
					continue
				camera_residual_file = os.path.join(frame_folder, camera_data["residual_path"])
				camera_data["sharpness"] = cv2.Laplacian(cv2.cvtColor(cv2.imread(camera_residual_file), cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()
				camera_data["file_path"] = os.path.relpath(camera_residual_file, frame_residual_folder)
				del camera_data["residual_path"]
			if frame > 0:
				with open(os.path.join(frame_residual_folder, "transforms.json"), "w") as outfile:
					json.dump(frame_data, outfile, indent=2)
	OUT_PATH = os.path.join(VIDEO_FOLDER, "transforms.json")
	print(f"writing {OUT_PATH}...")
	with open(OUT_PATH, "w") as outfile:
		json.dump(all_frame_data, outfile, indent=2)
