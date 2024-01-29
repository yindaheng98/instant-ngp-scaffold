#!/bin/bash
command() {
    echo $1 $2 start
    for i in {2..101}
    do
    python3 /volume/scripts/eval.py \
        --load_snapshot results/stnerf-taekwondo/frame${i}T=${1}T_density=${2}-snapshotsimulate.bson \
        --test_transforms data/nerf/taekwondo/frame${i}/transforms.json
    done
    echo $1 $2 complete
}

command 1.000000 1.000000

command 1.000000 0.500000
command 0.500000 1.000000
command 0.500000 0.500000

command 1.000000 0.100000
command 0.100000 1.000000

command 0.100000 0.500000
command 0.500000 0.100000
command 0.400000 0.100000
command 0.300000 0.100000
command 0.200000 0.100000
command 0.100000 0.100000

command 0.500000 0.050000
command 0.050000 0.500000

command 0.050000 0.100000
command 0.100000 0.050000
command 0.050000 0.050000

command 0.010000 0.100000
command 0.100000 0.010000
command 0.010000 0.010000