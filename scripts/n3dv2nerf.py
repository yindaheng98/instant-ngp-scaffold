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
	args = parser.parse_args()
	return args


# https://github.com/bmild/nerf/blob/18b8aebda6700ed659cb27a0c348b737a5f6ab60/load_llff.py#L125
def normalize(x):
    return x / np.linalg.norm(x)

# https://github.com/bmild/nerf/blob/18b8aebda6700ed659cb27a0c348b737a5f6ab60/load_llff.py#L128
def viewmatrix(z, up, pos):
    vec2 = normalize(z)
    vec1_avg = up
    vec0 = normalize(np.cross(vec1_avg, vec2))
    vec1 = normalize(np.cross(vec2, vec0))
    m = np.stack([vec0, vec1, vec2, pos], 1)
    return m

# https://github.com/bmild/nerf/blob/18b8aebda6700ed659cb27a0c348b737a5f6ab60/load_llff.py#L140
def poses_avg(poses):

    hwf = poses[0, :3, -1:]

    center = poses[:, :3, 3].mean(0)
    vec2 = normalize(poses[:, :3, 2].sum(0))
    up = poses[:, :3, 1].sum(0)
    c2w = np.concatenate([viewmatrix(vec2, up, center), hwf], 1)
    
    return c2w

# https://github.com/bmild/nerf/blob/18b8aebda6700ed659cb27a0c348b737a5f6ab60/load_llff.py#L166
def recenter_poses(poses):

    poses_ = poses+0
    bottom = np.reshape([0,0,0,1.], [1,4])
    c2w = poses_avg(poses)
    c2w = np.concatenate([c2w[:3,:4], bottom], -2)
    bottom = np.tile(np.reshape(bottom, [1,1,4]), [poses.shape[0],1,1])
    poses = np.concatenate([poses[:,:3,:4], bottom], -2)

    poses = np.linalg.inv(c2w) @ poses
    poses_[:,:3,:4] = poses[:,:3,:4]
    poses = poses_
    return poses


if __name__ == "__main__":
	args = parse_args()
	AABB_SCALE = int(args.aabb_scale)
	FRAMES = 300
	SKIP_EARLY = 0
	VIDEO_FOLDER = args.path
	camera_folders = []
	for folder in os.listdir(VIDEO_FOLDER):
		m = re.findall(r"^cam([0-9]+)$", folder)
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

	# https://github.com/bmild/nerf/blob/master/load_llff.py#L243
	poses_arr = np.load(os.path.join(VIDEO_FOLDER, 'poses_bounds.npy')).astype(np.float64)
	poses = poses_arr[:, :-2].reshape([-1, 3, 5]).transpose([1,2,0])
	poses = np.concatenate([poses[:, 1:2, :], -poses[:, 0:1, :], poses[:, 2:, :]], 1)
	poses = np.moveaxis(poses, -1, 0)
	poses = recenter_poses(poses)
	c2w = poses[:, :3, :4]
	hwf = poses[:, :3, 4]

	pos = c2w[:, :, 3]
	pos = pos - pos.mean(axis=0)
	scale = (pos.max(axis=0) - pos.min(axis=0)).max()
	pos = pos / scale * 2
	pos[:, 2] += 1
	pos = pos * AABB_SCALE * 0.52
	c2w[:, :, 3] = pos
	
	Ts = np.concatenate([c2w, np.zeros_like(c2w, shape=(c2w.shape[0], 1, 4))], axis=1)
	Ts[:, 3, 3] = 1

	h, w, f = hwf[:, 0], hwf[:, 1], hwf[:, 2]
	Ks = np.zeros_like(Ts, shape=(Ts.shape[0], 3, 3))
	Ks[:, 2, 2] = 1
	Ks[:, 0, 0] = f
	Ks[:, 1, 1] = f
	Ks[:, 0, 2] = 0.5*w
	Ks[:, 1, 2] = 0.5*h
	
	all_frame_data = {
		"is_fisheye": False, # should match the sence scale
		"aabb_scale": AABB_SCALE, # should match the sence scale
		"frames": []
	}
	for frame, camera_files in enumerate(video_files):
		frame_folder = os.path.join(VIDEO_FOLDER, "frame%03d" % (frame + 1))
		cameras_data = []
		for camera_file, K, T in zip(camera_files, Ks, Ts):
			frame_data = {
				"is_fisheye": False, # should match the sence scale
				"aabb_scale": AABB_SCALE, # should match the sence scale
			}
			img = cv2.imread(camera_file)
			h, w, _ = img.shape
			b = cv2.Laplacian(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()
			c2w = np.copy(T)
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
			}
			cameras_data.append({
				"file_path": os.path.relpath(camera_file, frame_folder),
				**camera_data
			})
			all_frame_data["frames"].append({
				"file_path": camera_file,
				**camera_data
			})
		frame_data["frames"] = cameras_data
		OUT_PATH = os.path.join(frame_folder, "transforms.json")
		os.makedirs(frame_folder, exist_ok=True)
		print(f"writing {OUT_PATH}...")
		with open(OUT_PATH, "w") as outfile:
			json.dump(frame_data, outfile, indent=2)
	OUT_PATH = os.path.join(VIDEO_FOLDER, "transforms.json")
	print(f"writing {OUT_PATH}...")
	with open(OUT_PATH, "w") as outfile:
		json.dump(all_frame_data, outfile, indent=2)
