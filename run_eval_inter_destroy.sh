#!/bin/bash
command() {
    echo $4 $5 start
    for i in `seq $1 $2 $3`
    do
    python3 /volume/scripts/eval.py \
        --load_snapshot results/$5/frame${i}${4}.bson \
        --test_transforms $6/frame${i}/transforms.json
    done
    echo $4 $5 complete
}

command 2 10 100 "T=0.100000T_density=0.100000-nosimulationdestroy" "stnerf-taekwondo" "data/nerf/taekwondo"
command 2 10 100 "-fp16destroy" "stnerf-taekwondo" "data/nerf/taekwondo"
command 2 10 100 "T=0.100000T_density=0.100000-nosimulationdestroy" "stnerf-walking" "data/nerf/walking"
command 2 10 100 "-fp16destroy" "stnerf-walking" "data/nerf/walking"
command 2 10 100 "T=0.100000T_density=0.100000-nosimulationdestroy" "coffee_martini" "data/nerf/coffee_martini"
command 2 10 100 "-fp16destroy" "coffee_martini" "data/nerf/coffee_martini"
command 2 10 100 "T=0.100000T_density=0.100000-nosimulationdestroy" "flame_steak" "data/nerf/flame_steak"
command 2 10 100 "-fp16destroy" "flame_steak" "data/nerf/flame_steak"
command 2 10 100 "T=0.100000T_density=0.100000-nosimulationdestroy" "sear_steak" "data/nerf/sear_steak"
command 2 10 100 "-fp16destroy" "sear_steak" "data/nerf/sear_steak"
