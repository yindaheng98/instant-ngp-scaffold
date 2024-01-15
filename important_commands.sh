python3 scripts/stnerf2nerf.py --aabb_scale 8 --path data/nerf/walking
python3 scripts/train_seq.py --steps 10000 --start 1 --end 75 --dataformat "data/nerf/walking/frame%d" --saveformat "results/stnerf-walking/frame%d.bson" --executable "./instant-ngp-train"
python3 scripts/train_seq.py --steps 10000 --start 1 --end 101 --dataformat "data/nerf/taekwondo/frame%d" --saveformat "results/stnerf-taekwondo/frame%d.bson" --executable "./instant-ngp-train"
