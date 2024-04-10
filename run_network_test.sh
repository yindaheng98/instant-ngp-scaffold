#!/bin/bash
command0() {
    ./build/instant-ngp-replay \
        --start $1 --end $2 \
        --load_snapshot results/$3/frame1.bson \
        --init results/$3/intra/frame1.bson \
        --frameformat results/$3/intra/frame%d.bson \
        --savecam $4 \
        --gethit results/$3/gridhit/M=$5/$6/frame%d.bson \
        --M_blimit $5 \
        --save_image results/$3/gridhit/M=$5/$6/img/gt/%d.bin
}
command1() {
    ./build/instant-ngp-replay \
        --start $1 --end $2 \
        --load_snapshot results/$3/frame1.bson \
        --init results/$3/intra/frame1.bson \
        --frameformat results/$3/gridhit/M=$5/$6/frame%d.bson \
        --savecam $4 --directcam \
        --M_blimit $5 \
        --save_image results/$3/gridhit/M=$5/$6/img/lr/%d.bin
}
command2() {
    python scripts/eval_cameras.py \
        --start $1 --end $2 \
        --modelformat results/$3/gridhit/M=$5/$6/frame%d.bson \
        --gtformat results/$3/gridhit/M=$5/$6/img/gt/%d.bin \
        --lrformat results/$3/gridhit/M=$5/$6/img/lr/%d.bin \
        --save results/$3/gridhit/M=$5/$6"_result.json" && \
        rm -rf results/$3/gridhit/M=$5/$6
}
command0 2 100 discussion-regularization-1e-7 camera/discussion.txt 200000 cam
command1 2 100 discussion-regularization-1e-7 camera/discussion.txt 200000 cam
command2 2 300 discussion-regularization-1e-7 camera/discussion.txt 200000 cam
command0 2 100 stepin-regularization-1e-7 camera/stepin.txt 200000 cam
command1 2 100 stepin-regularization-1e-7 camera/stepin.txt 200000 cam
command2 2 300 stepin-regularization-1e-7 camera/stepin.txt 200000 cam
command0 2 100 trimming-regularization-1e-7 camera/trimming.txt 200000 cam
command1 2 100 trimming-regularization-1e-7 camera/trimming.txt 200000 cam
command2 2 300 trimming-regularization-1e-7 camera/trimming.txt 200000 cam
command0 2 100 vrheadset-regularization-1e-7 camera/vrheadset.txt 200000 cam
command1 2 100 vrheadset-regularization-1e-7 camera/vrheadset.txt 200000 cam
command2 2 300 vrheadset-regularization-1e-7 camera/vrheadset.txt 200000 cam
command0 2 100 stnerf-taekwondo-regularization-1e-7 camera/stnerf-taekwondo.txt 200000 cam
command1 2 100 stnerf-taekwondo-regularization-1e-7 camera/stnerf-taekwondo.txt 200000 cam
command2 2 300 stnerf-taekwondo-regularization-1e-7 camera/stnerf-taekwondo.txt 200000 cam
command0 2 75 stnerf-walking-regularization-1e-7 camera/stnerf-walking.txt 200000 cam
command1 2 75 stnerf-walking-regularization-1e-7 camera/stnerf-walking.txt 200000 cam
command2 2 225 stnerf-walking-regularization-1e-7 camera/stnerf-walking.txt 200000 cam
command0 2 100 coffee_martini-regularization-1e-7 camera/coffee_martini.txt 200000 cam
command1 2 100 coffee_martini-regularization-1e-7 camera/coffee_martini.txt 200000 cam
command2 2 300 coffee_martini-regularization-1e-7 camera/coffee_martini.txt 200000 cam
command0 2 100 flame_steak-regularization-1e-7 camera/flame_steak.txt 200000 cam
command1 2 100 flame_steak-regularization-1e-7 camera/flame_steak.txt 200000 cam
command2 2 300 flame_steak-regularization-1e-7 camera/flame_steak.txt 200000 cam
command0 2 100 sear_steak-regularization-1e-7 camera/sear_steak.txt 200000 cam
command1 2 100 sear_steak-regularization-1e-7 camera/sear_steak.txt 200000 cam
command2 2 300 sear_steak-regularization-1e-7 camera/sear_steak.txt 200000 cam
