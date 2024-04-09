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
        --save results/$3/gridhit/M=$5/$6"_result.json"
}
command0 2 100 stnerf-taekwondo-regularization-none camera/stnerf-taekwondo-1.txt 200000 cam1
command1 2 100 stnerf-taekwondo-regularization-none camera/stnerf-taekwondo-1.txt 200000 cam1
command2 2 100 stnerf-taekwondo-regularization-none camera/stnerf-taekwondo-1.txt 200000 cam1
command0 2 100 stnerf-taekwondo-regularization-1e-7 camera/stnerf-taekwondo-1.txt 200000 cam1
command1 2 100 stnerf-taekwondo-regularization-1e-7 camera/stnerf-taekwondo-1.txt 200000 cam1
command2 2 100 stnerf-taekwondo-regularization-1e-7 camera/stnerf-taekwondo-1.txt 200000 cam1
