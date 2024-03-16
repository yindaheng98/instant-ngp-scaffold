#!/bin/bash
command() {
    build/instant-ngp ./data/$1/frame1 \
        --trainingcam \
        --start 1 --end 100 \
        --load_snapshot ./results/stnerf-taekwondo-regularization-none/frame1.bson \
        --init ./results/stnerf-taekwondo-regularization-none/intra/frame1.bson \
        --frameformat ./results/stnerf-taekwondo-regularization-none/intra/frame%d.bson \
        --savecam ./data/$1/camera.txt
}
command nerf/taekwondo
command nerf/walking
