#!/bin/bash
command() {
    echo $1 $2 $3 $4 $5 $6 start
    for i in `seq $2 $3 $4`
    do
    python scripts/eval.py \
        --load_snapshot results/$5/inter/T=0.010000L=$1/frame${i}-snapshotsimulate.bson \
        --test_transforms $6/frame${i}/transforms.json \
        --save_results results/$5/inter/T=0.010000L=$1/quality/frame${i}.json
    done
    echo $1 $2 $3 $4 $5 $6 complete
}

doall() {
    ARGS=$1
    command 0.2 $ARGS
    command 0.4 $ARGS
    command 0.6 $ARGS
    command 0.8 $ARGS
    command 1.0 $ARGS
}

doall "2 5 101 stnerf-taekwondo-regularization-none data/nerf/taekwondo"
doall "2 5 101 stnerf-taekwondo-regularization-1e-6 data/nerf/taekwondo"
doall "2 5 101 stnerf-taekwondo-regularization-1e-7 data/nerf/taekwondo"
doall "2 5 75 stnerf-walking-regularization-none data/nerf/walking"
doall "2 5 75 stnerf-walking-regularization-1e-6 data/nerf/walking"
doall "2 5 75 stnerf-walking-regularization-1e-7 data/nerf/walking"
doall "2 5 100 coffee_martini-regularization-none data/nerf/coffee_martini"
doall "2 5 100 coffee_martini-regularization-1e-6 data/nerf/coffee_martini"
doall "2 5 100 coffee_martini-regularization-1e-7 data/nerf/coffee_martini"
doall "2 5 100 flame_steak-regularization-none data/nerf/flame_steak"
doall "2 5 100 flame_steak-regularization-1e-6 data/nerf/flame_steak"
doall "2 5 100 flame_steak-regularization-1e-7 data/nerf/flame_steak"
doall "2 5 100 sear_steak-regularization-none data/nerf/sear_steak"
doall "2 5 100 sear_steak-regularization-1e-6 data/nerf/sear_steak"
doall "2 5 100 sear_steak-regularization-1e-7 data/nerf/sear_steak"
