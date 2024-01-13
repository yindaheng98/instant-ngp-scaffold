python3 scripts/stnerf2nerf.py --aabb_scale 8 --path data/nerf/walking
python3 scripts/train_seq.py --start 1 --end 75 --dataformat "data/nerf/walking/frame%d" --saveformat "results/stnerf-walking/frame%d.bson" --executable "./instant-ngp-train" --steps 1000
