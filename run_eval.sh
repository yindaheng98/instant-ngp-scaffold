#!/bin/bash
for i in {2..101}
do
python3 /volume/scripts/eval.py \
    --load_snapshot results/stnerf-taekwondo/frame${i}.bson \
    --test_transforms data/nerf/taekwondo/frame${i}/transforms.json
for p in T=0.010000T_density=0.010000 T=0.010000T_density=0.100000 T=0.050000T_density=0.050000 T=0.050000T_density=0.100000 T=0.100000T_density=0.100000 T=1.000000T_density=1.000000
do
python3 /volume/scripts/eval.py \
    --load_snapshot results/stnerf-taekwondo/frame${i}${p}-snapshotsimulate.bson \
    --test_transforms data/nerf/taekwondo/frame${i}/transforms.json
done
done
