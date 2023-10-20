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

	parser.add_argument("--aabb_scale", default=32, help="large scene scale factor")
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

# TODO: scale the sence using a smarter methods
# Exported by colmap2nerf
scale_matrixs = [
	[[0.4969242140516516, -0.03047425087102452, 0.8672586958491709, 5.057854883543904], [-0.002219976139035497, -0.999424582044111, -0.03384636635212092, -0.13206258820166752], [-0.8677911022793547, -0.014893785386850223, 0.49670592704534194, 1.9612174987525168], [0.0, 0.0, 0.0, 1.0]],
	[[0.23981436257635957, -0.038893268842789985, 0.9700393729865042, 4.709230016348499], [0.022846049715884272, -0.9986943791733215, -0.045690207083572916, -0.1421626004968038], [-0.970549910882736, -0.03311873562925429, 0.23861269839626664, 0.8538285979683513], [0.0, 0.0, 0.0, 1.0]],
	[[-0.011696124435674603, 0.021170031257073164, 0.9997074724403604, 4.13081303672776], [-0.012782312220933515, -0.9996973345846111, 0.0210202693145404, 0.14213672561679058], [-0.9998498953180383, 0.01253271735668059, -0.011963186372322271, -0.09468266172027129], [0.0, 0.0, 0.0, 1.0]],
	[[-0.2781997825515167, -0.01184461101715443, 0.9604501997404506, 3.2372920369652842], [0.03762286642982449, -0.9992909919705573, -0.0014259352889543244, 0.011204983523028707], [-0.9597861224825269, -0.03573819468992765, -0.2784481648894041, -1.013762241042576], [0.0, 0.0, 0.0, 1.0]],
	[[-0.4895639729831684, 0.050956247223983585, 0.8704772123548181, 2.0934239738945197], [-0.019539825159589873, -0.9986814454776874, 0.047471735745334274, 0.13625555985159116], [-0.8717484221895744, -0.006231479021094344, -0.4899141323531218, -1.7545528958615015], [0.0, 0.0, 0.0, 1.0]],
	[[-0.7164770333255929, 0.09288979696661019, 0.6913986884131812, 0.6102420221660978], [-0.05559130094565799, -0.9955458962564616, 0.07614443978015058, 0.1713007293152793], [-0.6953921684753432, -0.01611998975696624, -0.7184496349457856, -2.3293638511544925], [0.0, 0.0, 0.0, 1.0]],
	[[-0.8744163834346674, 0.07238761206179159, 0.47974578893799064, -1.0067649358146773], [-0.04400280268750559, -0.9965642977065806, 0.0701666152495649, 0.09365514198259758], [-0.48317671895259307, -0.04024467865354819, -0.8745974068695381, -2.5498708388343485], [0.0, 0.0, 0.0, 1.0]],
	[[-0.9572539609820564, 0.11763214559128564, 0.2642489971790257, -2.6375923930396183], [-0.09942088737371507, -0.9917175584019615, 0.08131280043400728, -0.009997917537788503], [-0.2716253694695336, -0.051565130506854656, -0.9610206532522244, -2.4425440319406517], [0.0, 0.0, 0.0, 1.0]],
	[[-0.9923812379051097, 0.12245725034545048, 0.013553615521654934, -4.278496520316708], [-0.12104191212896118, -0.9895641472806107, 0.07817706779042154, -0.12440713119635599], [-0.022985520746253374, -0.0759408997706522, -0.996847353198793, -2.0042527987042567], [0.0, 0.0, 0.0, 1.0]],
	[[-0.9592184457296109, 0.1596978167350795, -0.23323074562255688, -5.762881509565511], [-0.17796899399321245, -0.982242906785284, 0.05937936721099894, -0.38326446080234755], [0.21960649023057072, -0.09846562549128837, -0.9706067741609047, -1.292401578867242], [0.0, 0.0, 0.0, 1.0]],
	[[-0.8748352004823636, 0.15894973144796104, -0.45760064998940914, -7.197877385097071], [-0.19884196888782216, -0.9792145657801737, 0.04000881872909408, -0.5799239148645561], [0.44172983078846967, -0.1259913371621785, -0.8882572485231441, -0.31843557525287647], [0.0, 0.0, 0.0, 1.0]],
	[[-0.7350007203436604, 0.1151162792236206, -0.6682231538585993, -8.40197579356079], [-0.1757693506068642, -0.9841437832708833, 0.023793890809523467, -0.6280304515933421], [0.6548885985299076, -0.13494167669897134, -0.7435803032677988, 0.9704485872374575], [0.0, 0.0, 0.0, 1.0]],
	[[-0.521109699892665, 0.13098397029067677, -0.8433788473782458, -9.308082784729752], [-0.22480691521521784, -0.9743242181551925, -0.012416472567525406, -1.0538551653468204], [0.8233507949545946, -0.18312705274347169, -0.537175903223609, 2.4915664374074353], [0.0, 0.0, 0.0, 1.0]],
	[[-0.29669877128731326, 0.1282656834166644, -0.9463179981245351, -9.887940797624044], [-0.22236884541567414, -0.97297904072914, -0.06216013910556283, -1.3120204614194664], [0.9287205907636602, -0.19198880374335522, -0.31720397779976256, 4.055301590207091], [0.0, 0.0, 0.0, 1.0]],
	[[0.01690530290173301, 0.16885858429364045, -0.9854953014825744, -9.992313486830367], [-0.25559223786761154, -0.9521585852413854, -0.16753100159738202, -2.0998696219771804], [0.9666368597767053, -0.2547171118413842, -0.027062414148602394, 6.069284783906489], [0.0, 0.0, 0.0, 1.0]],
	[[0.30754909620411214, 0.1505584641009406, -0.9395454764468504, -9.616789406118532], [-0.21045410627496428, -0.9521861426898278, -0.22147374296903635, -2.377658548029269], [0.927966929679765, -0.26584525303337425, 0.2611583405975031, 7.90543616709623], [0.0, 0.0, 0.0, 1.0]]
]

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
		camera_files_dict = {}
		for camera_file in os.listdir(os.path.join(frame_folder, 'images')):
			m = re.findall(r"^([0-9]+)", camera_file)
			if len(m) != 1:
				continue
			camera = int(m[0])
			camera_files_dict[camera] = os.path.join(frame_folder, 'images', camera_file)
		camera_files = [None] * len(camera_files_dict)
		for camera, camera_file in camera_files_dict.items():
			camera_files[camera] = camera_file
		assert None not in camera_files and len(camera_files) == CAMERAS
		video_files[frame] = camera_files
	assert None not in video_files

	# https://github.com/DarlingHang/st-nerf/blob/e0c1c32b09d90101218410443193ddabc1f66d2f/data/datasets/frame_dataset.py#L25C23-L25C23
	camposes = np.loadtxt(os.path.join('pose', 'RT_c2w.txt'))
	Ts = campose_to_extrinsic(camposes)
	Ks = read_intrinsics(os.path.join('pose', 'K.txt'))
	# TODO: scale the sence using a smarter methods
	# TODO: c2w format LLFF/OpenGL DRB or RUB to OpenCV/Colmap RDF
	Ts = np.array([np.dot(transform_matrix, inverse_matrix)for transform_matrix, inverse_matrix in zip(Ts, scale_matrixs)])
	
	for frame, frame_folder in frame_folders.items():
		camera_files = video_files[frame]
		frame_data = {
			"camera_angle_x": 1.1168212628965795, # should match the sence scale
			"camera_angle_y": 0.6762639070477788, # should match the sence scale
			"fl_x": 1536.6450408222427, # should match the sence scale
			"fl_y": 1535.6768932703187, # should match the sence scale
			"k1": -0.21333396828236248, # should match the sence scale
			"k2": 0.0765714553769733, # should match the sence scale
			"k3": 0, # should match the sence scale
			"k4": 0, # should match the sence scale
			"p1": -0.0006305142879307653, # should match the sence scaletch the sence scale
			"p2": 0.0017951435750177375,
			"is_fisheye": False, # should match the sence scale
			"cx": 974.3300736643988, # should match the sence scale
			"cy": 547.2588220395855, # should match the sence scale
			"w": 1920.0, # should match the sence scale
			"h": 1080.0, # should match the sence scale
			"aabb_scale": AABB_SCALE, # should match the sence scale
		}
		cameras_data = []
		for camera_file, K, T in zip(camera_files, Ks, Ts):
			w, h, _ = cv2.imread(camera_file).shape
			c2w = T
			# TODO: c2w format LLFF/OpenGL DRB or RUB to OpenCV/Colmap RDF
			# st-nerf c2w[[x,y,z,camera], :] to instant-ngp c2w[[x,z,y,camera], :]
			c2w = c2w[[0,2,1,3], :]
			cameras_data.append({
				"file_path": os.path.relpath(camera_file, frame_folder),
				"transform_matrix": c2w.tolist(),
				# "fl_x": K[0,0], # should match the sence scale
				# "fl_y": K[1,1], # should match the sence scale
				# "cx": K[0,2], # should match the sence scale
				# "cy": K[1,2], # should match the sence scale
				# "w": w,
				# "h": h,
			})
		frame_data["frames"] = cameras_data
		OUT_PATH = os.path.join(frame_folder, "transforms-origin.json")
		print(f"writing {OUT_PATH}...")
		with open(OUT_PATH, "w") as outfile:
			json.dump(frame_data, outfile, indent=2)
