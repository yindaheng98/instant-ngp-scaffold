python3 scripts/stnerf2nerf.py --aabb_scale 8 --path data/nerf/walking
python3 scripts/train_seq.py \
    --steps 10000 --start 1 --end 101 \
    --dataformat "data/nerf/taekwondo/frame%d" \
    --saveformat "results/stnerf-taekwondo/frame%d.bson" \
    --executable "./instant-ngp-train"
python3 scripts/train_seq.py \
    --steps 10000 --start 1 --end 101 \
    --dataformat "data/nerf/taekwondo/frame%d" \
    --saveformat "results/stnerf-taekwondo/frame%d-nofreeze.bson" \
    --executable "./instant-ngp-train" \
    --no_freeze
./instant-ngp-origin --load_snapshot results/stnerf-taekwondo/frame2T=0.100000T_density=0.100000-snapshotsimulate.bson --no-train data/nerf/taekwondo/frame2
python3 scripts/n3dv2imgs.py --path data/nerf/coffee_martini --exec ffmpeg > temp.sh && cat temp.sh && ./temp.sh
