#!/bin/bash
command() {
    echo $1 $2 start
    for i in {2..101}
    do
    python3 /volume/scripts/eval.py \
        --load_snapshot results/stnerf-taekwondo/frame${i}${1}.bson \
        --test_transforms data/nerf/taekwondo/frame${i}/transforms.json
    done
    echo $1 $2 complete
}

command "-T=0.100000nosimulationdestroy"
command "-fp16destroy"
