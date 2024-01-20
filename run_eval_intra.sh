#!/bin/bash
for i in {2..101}
do
python3 /volume/scripts/eval.py \
    --load_snapshot results/stnerf-taekwondo/frame${i}.bson \
    --test_transforms data/nerf/taekwondo/frame${i}/transforms.json
done
