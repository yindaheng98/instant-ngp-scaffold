#!/bin/bash
command0() {
    echo 0 start
    python ./scripts/parse_seq_size.py \
        --start $2 --end $3 \
        --saveformat results/$4/frame%d.bson \
        --initexportformat results/$4/frame%d-intra.json \
        -T 0
    echo 0 complete
}

command() {
    echo $1 start
    python ./scripts/parse_seq_size.py \
        --start $2 --end $3 \
        --saveformat results/$4/frame%d.bson \
        --intraexportformat results/$4/frame%\(i\)dT=%\(T\)f-intra.json \
        --interexportformat results/$4/frame%\(i\)dT=%\(T\)f-inter.json \
        -T $1
    echo $1 complete
}

doall() {
    ARGS="$1"
    echo Start Group:
    command0 0 $ARGS &
    command 1 $ARGS &
    command 0.9 $ARGS &
    command 0.8 $ARGS &
    command 0.7 $ARGS &
    command 0.6 $ARGS &
    command 0.5 $ARGS &
    command 0.4 $ARGS &
    command 0.3 $ARGS &
    command 0.2 $ARGS &
    command 0.1 $ARGS &
    command 0.05 $ARGS &
    command 0.01 $ARGS &
    wait
}

doall "1 101 stnerf-taekwondo-regularization-1e-6"
doall "1 75 stnerf-walking-regularization-1e-6"
doall "1 100 coffee_martini-regularization-1e-6"
doall "1 100 flame_steak-regularization-1e-6"
doall "1 100 sear_steak-regularization-1e-6"
