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
from textwrap import indent
import commentjson as json

import numpy as np

from common import *
from scenes import *

from tqdm import tqdm
import imageio
import matplotlib.pyplot as plt

import pyngp as ngp # noqa

def parse_args():
	parser = argparse.ArgumentParser(description="Run instant neural graphics primitives with additional configuration & output options")


	parser.add_argument("--cameras", type=str, required=True, help="Path to the cameras.")
	parser.add_argument("--network", default="", help="Path to the network config. Uses the scene's default if unspecified.")

	parser.add_argument("--fmt_snapshot", "--snapshot", required=True, help="Load this snapshot before training. recommended extension: .ingp/.bson")
	parser.add_argument("--fmt_snapshot_gt", "--snapshot_gt", required=True, help="Load this snapshot before training. recommended extension: .ingp/.bson")

	parser.add_argument("--max_test", type=int, default=16, help="Maximum test images")
	parser.add_argument("--nerf_compatibility", action="store_true", help="Matches parameters with original NeRF. Can cause slowness and worse results on some scenes, but helps with high PSNR on synthetic scenes.")
	parser.add_argument("--test_transforms", default="", help="Path to a nerf style transforms json from which we will compute PSNR.")
	parser.add_argument("--exposure", default=0.0, type=float, help="Controls the brightness of the image. Positive numbers increase brightness, negative numbers decrease it.")

	parser.add_argument("--sharpen", default=0, help="Set amount of sharpening applied to NeRF training images. Range 0.0 to 1.0.")
	parser.add_argument("--write_image", default=None, help="Write image to this dir.")
	parser.add_argument("--external_mask_fmt", default=None, help="Specify your mask.")

	return parser.parse_args()

def get_scene(scene):
	for scenes in [scenes_sdf, scenes_nerf, scenes_image, scenes_volume]:
		if scene in scenes:
			return scenes[scene]
	return None

spp = 8

def eval(testbed, path_snapshot, path_snapshot_gt, camera):
	print("eval", path_snapshot, path_snapshot_gt, camera)

	testbed.load_snapshot(path_snapshot)
	testbed.camera_matrix = camera
	testbed.render_ground_truth = False
	res_image = testbed.render(1920, 1080, spp, True)
	A = np.clip(linear_to_srgb(res_image[...,:3]), 0.0, 1.0)
	# plt.imshow(A)
	# plt.show()

	testbed.load_snapshot(path_snapshot_gt)
	testbed.camera_matrix = camera
	testbed.render_ground_truth = False
	ref_image = testbed.render(1920, 1080, spp, True)
	R = np.clip(linear_to_srgb(ref_image[...,:3]), 0.0, 1.0)
	# plt.imshow(R)
	# plt.show()

	mse = float(compute_error("MSE", A, R))
	ssim = float(compute_error("SSIM", A, R))
	psnr = mse2psnr(mse)
	print(psnr, ssim)


if __name__ == "__main__":
	args = parse_args()

	testbed = ngp.Testbed()
	testbed.root_dir = ROOT_DIR

	if testbed.mode == ngp.TestbedMode.Sdf:
		testbed.tonemap_curve = ngp.TonemapCurve.ACES

	testbed.nerf.sharpen = float(args.sharpen)
	testbed.exposure = args.exposure
	testbed.shall_train = False


	testbed.nerf.render_with_lens_distortion = True

	if args.nerf_compatibility:
		print(f"NeRF compatibility mode enabled")

		# Prior nerf papers accumulate/blend in the sRGB
		# color space. This messes not only with background
		# alpha, but also with DOF effects and the likes.
		# We support this behavior, but we only enable it
		# for the case of synthetic nerf data where we need
		# to compare PSNR numbers to results of prior work.
		testbed.color_space = ngp.ColorSpace.SRGB

		# No exponential cone tracing. Slightly increases
		# quality at the cost of speed. This is done by
		# default on scenes with AABB 1 (like the synthetic
		# ones), but not on larger scenes. So force the
		# setting here.
		testbed.nerf.cone_angle_constant = 0

		# Match nerf paper behaviour and train on a fixed bg.
		testbed.nerf.training.random_bg_color = False

	# Evaluate metrics on black background
	testbed.background_color = [0.0, 0.0, 0.0, 1.0]

	# Prior nerf papers don't typically do multi-sample anti aliasing.
	# So snap all pixels to the pixel centers.
	testbed.snap_to_pixel_centers = True
	spp = 8

	testbed.nerf.render_min_transmittance = 1e-4

	testbed.shall_train = False

	cameras = []
	with open(args.cameras, "r", encoding="utf8") as f:
		for line in f.readlines():
			cameras.append(json.loads(line))
	for i, camera in enumerate(cameras):
		path_snapshot = args.fmt_snapshot % i
		path_snapshot_gt = args.fmt_snapshot_gt % camera["frame"]
		eval(testbed, path_snapshot, path_snapshot_gt, camera["views"][0]["camera0"])
