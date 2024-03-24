./instant-ngp-train --step=30000 -c configs/nerf/base_16 --save_snapshot results/basketball-base_16-frame0.bson data/nerf/basketball/img/0
./instant-ngp-train --step=30000 -c configs/nerf/base_16 --save_snapshot results/basketball-base_16-mask-frame0.bson data/nerf/basketball/img/0/mask
./instant-ngp-train --step=30000 -c configs/nerf/base_15 --save_snapshot results/basketball-base_15-frame0.bson data/nerf/basketball/img/0
./instant-ngp-train --step=30000 -c configs/nerf/base_15 --save_snapshot results/basketball-base_15-mask-frame0.bson data/nerf/basketball/img/0/mask
python scripts/eval.py --load_snapshot results/basketball-base_16-frame0.bson --write_image results/eval_images/basketball-base_16-frame0 --test_transforms data/nerf/basketball/img/0/transforms.json
python scripts/eval.py --load_snapshot results/basketball-base_16-mask-frame0.bson --write_image results/eval_images/basketball-base_16-mask-frame0 --test_transforms data/nerf/basketball/img/0/mask/transforms.json
python scripts/eval.py --load_snapshot results/basketball-base_15-frame0.bson --write_image results/eval_images/basketball-base_15-frame0 --test_transforms data/nerf/basketball/img/0/transforms.json
python scripts/eval.py --load_snapshot results/basketball-base_15-mask-frame0.bson --write_image results/eval_images/basketball-base_15-mask-frame0 --test_transforms data/nerf/basketball/img/0/mask/transforms.json

python scripts/eval.py --load_snapshot results/basketball-frame0.bson --write_image results/eval_images/basketball-frame0 --test_transforms data/nerf/basketball/img/0/transforms.json
