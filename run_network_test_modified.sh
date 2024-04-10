#!/bin/bash
command0() {
    ./build/instant-ngp-replay \
        --start $1 --end $2 \
        --load_snapshot results/$3/frame1.bson \
        --init results/$3/intra/frame1.bson \
        --frameformat results/$3/intra/frame%d.bson \
        --savecam $4 \
        --gethit results/$3/gridhit/M=$5/$6/frame%d$7.bson \
        --M_blimit $5 \
        --save_image results/$3/gridhit/M=$5/$6/img/gt/%d$7.bin
}
command1() {
    ./build/instant-ngp-replay \
        --start $1 --end $2 \
        --load_snapshot results/$3/frame1.bson \
        --init results/$3/intra/frame1.bson \
        --frameformat results/$3/gridhit/M=$5/$6/frame%d$7.bson \
        --savecam $4 --directcam \
        --M_blimit $5 \
        --save_image results/$3/gridhit/M=$5/$6/img/lr/%d$7.bin
}
command2() {
    python scripts/eval_cameras.py \
        --start $1 --end $2 \
        --modelformat results/$3/gridhit/M=$5/$6/frame%d$7.bson \
        --gtformat results/$3/gridhit/M=$5/$6/img/gt/%d$7.bin \
        --lrformat results/$3/gridhit/M=$5/$6/img/lr/%d$7.bin \
        --save results/$3/gridhit/M=$5/$6"-modified_result.json"
}
command0 2 100 sear_steak-regularization-1e-7 camera/sear_steak.txt 200000 cam -modified
command1 2 100 sear_steak-regularization-1e-7 camera/sear_steak.txt 200000 cam -modified
command2 2 300 sear_steak-regularization-1e-7 camera/sear_steak.txt 200000 cam -modified
