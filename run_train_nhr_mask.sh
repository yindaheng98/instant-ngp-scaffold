./instant-ngp-train --step=30000 --save_snapshot results/basketball-base16-frame0.bson data/nerf/basketball/img/0
./instant-ngp-train --step=30000 --save_snapshot results/basketball-base16-mask-frame0.bson data/nerf/basketball/img/0/mask
./instant-ngp-train --step=30000 --save_snapshot results/basketball-base15-frame0.bson data/nerf/basketball/img/0
./instant-ngp-train --step=30000 --save_snapshot results/basketball-base15-mask-frame0.bson data/nerf/basketball/img/0/mask
python scripts/eval.py --load_snapshot results/basketball-base16-frame0.bson --write_image results/eval_images/basketball-base16-frame0 --width 1024 --height 768 --test_transforms data/nerf/basketball/img/0/transforms.json
python scripts/eval.py --load_snapshot results/basketball-base16-mask-frame0.bson --write_image results/eval_images/basketball-base16-mask-frame0 --width 1024 --height 768 --test_transforms data/nerf/basketball/img/0/mask/transforms.json
python scripts/eval.py --load_snapshot results/basketball-base15-frame0.bson --write_image results/eval_images/basketball-base15-frame0 --width 1024 --height 768 --test_transforms data/nerf/basketball/img/0/transforms.json
python scripts/eval.py --load_snapshot results/basketball-base15-mask-frame0.bson --write_image results/eval_images/basketball-base15-mask-frame0 --width 1024 --height 768 --test_transforms data/nerf/basketball/img/0/mask/transforms.json
