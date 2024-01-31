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

doall() {
    ARGS=$1
    command 0.500000 0.100000 $ARGS
    command 0.400000 0.100000 $ARGS
    command 0.300000 0.100000 $ARGS
    command 0.200000 0.100000 $ARGS
    command 0.100000 0.100000 $ARGS
}

doall "2 5 75 stnerf-walking data/nerf/walking"
doall "2 5 100 coffee_martini data/nerf/coffee_martini"
doall "2 5 100 flame_steak data/nerf/flame_steak"
doall "2 5 100 sear_steak data/nerf/sear_steak"
