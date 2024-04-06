#!/bin/bash
command0() {
    echo $1 start
    python ./scripts/parse_seq_size.py \
        --start $2 --end $3 \
        --saveformat results/$4/frame%d.bson \
        --fullexportformat results/$4/size/frame%d.json \
        -T $1
    echo $1 complete
}

command1() {
    echo $1 start
    python ./scripts/parse_seq_size.py \
        --start $2 --end $3 \
        --saveformat results/$4/frame%d.bson \
        --interexportformat results/$4/size/frame%\(i\)dT=%\(T\)fL=%\(L\)s-inter.json \
        -T 0.01 -L $1
    echo $1 complete
}

doall() {
    ARGS="$1"
    echo Start Group:
    command0 0.0 $ARGS &
    command1 0.2 $ARGS &
    command1 0.4 $ARGS &
    command1 0.6 $ARGS &
    command1 0.8 $ARGS &
    command1 1.0 $ARGS &
    wait
}

doall "1 101 stnerf-taekwondo-regularization-none"
