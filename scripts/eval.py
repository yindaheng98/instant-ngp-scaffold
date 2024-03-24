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

import pyngp as ngp # noqa

def parse_args():
	parser = argparse.ArgumentParser(description="Run instant neural graphics primitives with additional configuration & output options")


	parser.add_argument("--network", default="", help="Path to the network config. Uses the scene's default if unspecified.")

	parser.add_argument("--load_snapshot", "--snapshot", required=True, help="Load this snapshot before training. recommended extension: .ingp/.bson")

	parser.add_argument("--nerf_compatibility", action="store_true", help="Matches parameters with original NeRF. Can cause slowness and worse results on some scenes, but helps with high PSNR on synthetic scenes.")
	parser.add_argument("--test_transforms", default="", help="Path to a nerf style transforms json from which we will compute PSNR.")
	parser.add_argument("--exposure", default=0.0, type=float, help="Controls the brightness of the image. Positive numbers increase brightness, negative numbers decrease it.")

	parser.add_argument("--sharpen", default=0, help="Set amount of sharpening applied to NeRF training images. Range 0.0 to 1.0.")
	parser.add_argument("--write_image", default=None, help="Write image to this dir.")

	return parser.parse_args()

def get_scene(scene):
	for scenes in [scenes_sdf, scenes_nerf, scenes_image, scenes_volume]:
		if scene in scenes:
			return scenes[scene]
	return None

if __name__ == "__main__":
	args = parse_args()

	testbed = ngp.Testbed()
	testbed.root_dir = ROOT_DIR

	if args.load_snapshot:
		scene_info = get_scene(args.load_snapshot)
		if scene_info is not None:
			args.load_snapshot = default_snapshot_filename(scene_info)
		testbed.load_snapshot(args.load_snapshot)
	elif args.network:
		testbed.reload_network_from_file(args.network)

	if testbed.mode == ngp.TestbedMode.Sdf:
		testbed.tonemap_curve = ngp.TonemapCurve.ACES

	testbed.nerf.sharpen = float(args.sharpen)
	testbed.exposure = args.exposure
	testbed.shall_train = False


	testbed.nerf.render_with_lens_distortion = True

	network_stem = os.path.splitext(os.path.basename(args.network))[0] if args.network else "base"
	if testbed.mode == ngp.TestbedMode.Sdf:
		setup_colored_sdf(testbed, args.scene)

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

	print("Evaluating test transforms from ", args.test_transforms)
	with open(args.test_transforms) as f:
		test_transforms = json.load(f)
	data_dir=os.path.dirname(args.test_transforms)
	totmse = 0
	totpsnr = 0
	totssim = 0
	totcount = 0
	minpsnr = 1000
	maxpsnr = 0

	# Evaluate metrics on black background
	testbed.background_color = [0.0, 0.0, 0.0, 1.0]

	# Prior nerf papers don't typically do multi-sample anti aliasing.
	# So snap all pixels to the pixel centers.
	testbed.snap_to_pixel_centers = True
	spp = 8

	testbed.nerf.render_min_transmittance = 1e-4

	testbed.shall_train = False
	testbed.load_training_data(args.test_transforms)

	allpsnr, allssim = [], []
	transform_frames = test_transforms["frames"]
	with tqdm(range(testbed.nerf.training.dataset.n_images), unit="images", desc=f"Rendering test frame") as t:
		for i in t:
			resolution = testbed.nerf.training.dataset.metadata[i].resolution
			testbed.render_ground_truth = True
			testbed.set_camera_to_training_view(i)
			ref_image = testbed.render(resolution[0], resolution[1], 1, True)
			testbed.render_ground_truth = False
			image = testbed.render(resolution[0], resolution[1], spp, True)
			transform_frame = transform_frames[i]
			if "mask_path" in transform_frame:
				transform_ref_mask_path = os.path.join(os.path.dirname(args.test_transforms), transform_frame["mask_path"])
				transform_mask = imageio.imread(transform_ref_mask_path).max(axis=2) == 0
				ref_image[transform_mask] = 0
				image[transform_mask] = 0
			
			if args.write_image:
				os.makedirs(args.write_image, exist_ok=True)
				write_image(os.path.join(args.write_image, os.path.basename(args.load_snapshot) + "%d.png" % i), image)

			A = np.clip(linear_to_srgb(image[...,:3]), 0.0, 1.0)
			R = np.clip(linear_to_srgb(ref_image[...,:3]), 0.0, 1.0)
			mse = float(compute_error("MSE", A, R))
			ssim = float(compute_error("SSIM", A, R))
			totssim += ssim
			totmse += mse
			psnr = mse2psnr(mse)
			totpsnr += psnr
			minpsnr = psnr if psnr<minpsnr else minpsnr
			maxpsnr = psnr if psnr>maxpsnr else maxpsnr
			totcount = totcount+1
			t.set_postfix(psnr = totpsnr/(totcount or 1))
			allpsnr.append(psnr)
			allssim.append(ssim)
	with open(args.load_snapshot + ".json", "w", encoding="utf8") as f:
		json.dump(dict(psnr=allpsnr, ssim=allssim), f, indent=2)