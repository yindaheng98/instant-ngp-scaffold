#!/bin/bash
command() {
    echo $1 $2 $3 $4 $5 $6 $7 start
    for i in `seq $3 $4 $5`
    do
    python3 /volume/scripts/eval.py \
        --load_snapshot results/$6/frame${i}T=${1}T_density=${2}-snapshotsimulate.bson \
        --test_transforms $7/frame${i}/transforms.json
    done
    echo $1 $2 $3 $4 $5 $6 $7 complete
}

command 1.000000 1.000000 2 10 101 stnerf-walking data/nerf/walking

command 1.000000 0.100000 2 10 101 stnerf-walking data/nerf/walking

command 0.500000 0.100000 2 10 101 stnerf-walking data/nerf/walking
command 0.400000 0.100000 2 10 101 stnerf-walking data/nerf/walking
command 0.300000 0.100000 2 10 101 stnerf-walking data/nerf/walking
command 0.200000 0.100000 2 10 101 stnerf-walking data/nerf/walking
command 0.100000 0.100000 2 10 101 stnerf-walking data/nerf/walking

# command 0.500000 0.050000 2 10 101 stnerf-walking data/nerf/walking

# command 0.050000 0.100000 2 10 101 stnerf-walking data/nerf/walking
# command 0.100000 0.050000 2 10 101 stnerf-walking data/nerf/walking
command 0.050000 0.050000 2 10 101 stnerf-walking data/nerf/walking

# command 0.010000 0.100000 2 10 101 stnerf-walking data/nerf/walking
command 0.100000 0.010000 2 10 101 stnerf-walking data/nerf/walking
command 0.010000 0.010000 2 10 101 stnerf-walking data/nerf/walking
