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
doall() {
    command0 $@
    command1 $@
    command2 $@
}
doall 2 100 discussion-regularization-1e-7 camera/discussion-1.txt 200000 cam1
doall 2 100 discussion-regularization-1e-7 camera/discussion-2.txt 200000 cam2
doall 2 100 discussion-regularization-1e-7 camera/discussion-3.txt 200000 cam3
doall 2 100 stepin-regularization-1e-7 camera/stepin-1.txt 200000 cam1
doall 2 100 stepin-regularization-1e-7 camera/stepin-2.txt 200000 cam2
doall 2 100 stepin-regularization-1e-7 camera/stepin-3.txt 200000 cam3
doall 2 100 trimming-regularization-1e-7 camera/trimming-1.txt 200000 cam1
doall 2 100 trimming-regularization-1e-7 camera/trimming-2.txt 200000 cam2
doall 2 100 trimming-regularization-1e-7 camera/trimming-3.txt 200000 cam3
doall 2 100 vrheadset-regularization-1e-7 camera/vrheadset-1.txt 200000 cam1
doall 2 100 vrheadset-regularization-1e-7 camera/vrheadset-2.txt 200000 cam2
doall 2 100 vrheadset-regularization-1e-7 camera/vrheadset-3.txt 200000 cam3
doall 2 100 stnerf-taekwondo-regularization-1e-7 camera/stnerf-taekwondo-1.txt 200000 cam1
doall 2 100 stnerf-taekwondo-regularization-1e-7 camera/stnerf-taekwondo-2.txt 200000 cam2
doall 2 100 stnerf-taekwondo-regularization-1e-7 camera/stnerf-taekwondo-3.txt 200000 cam3
doall 2 75 stnerf-walking-regularization-1e-7 camera/stnerf-walking-1.txt 200000 cam1
doall 2 75 stnerf-walking-regularization-1e-7 camera/stnerf-walking-2.txt 200000 cam2
doall 2 75 stnerf-walking-regularization-1e-7 camera/stnerf-walking-3.txt 200000 cam3
doall 2 100 coffee_martini-regularization-1e-7 camera/coffee_martini-1.txt 200000 cam1
doall 2 100 coffee_martini-regularization-1e-7 camera/coffee_martini-2.txt 200000 cam2
doall 2 100 coffee_martini-regularization-1e-7 camera/coffee_martini-3.txt 200000 cam3
doall 2 100 flame_steak-regularization-1e-7 camera/flame_steak-1.txt 200000 cam1
doall 2 100 flame_steak-regularization-1e-7 camera/flame_steak-2.txt 200000 cam2
doall 2 100 flame_steak-regularization-1e-7 camera/flame_steak-3.txt 200000 cam3
doall 2 100 sear_steak-regularization-1e-7 camera/sear_steak-1.txt 200000 cam1
doall 2 100 sear_steak-regularization-1e-7 camera/sear_steak-2.txt 200000 cam2
doall 2 100 sear_steak-regularization-1e-7 camera/sear_steak-3.txt 200000 cam3
