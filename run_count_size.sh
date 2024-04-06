#!/bin/bash
command() {
    echo $1 start
    python ./scripts/parse_seq_size.py \
        --start $2 --end $3 \
        --saveformat results/$4/frame%d.bson \
        --fullexportformat results/$4/size/frame%d.json \
        --interexportformat results/$4/size/frame%\(i\)dT=%\(T\)fL=%\(L\)s-inter.json \
        -T 0.01 -L $1
    echo $1 complete
}

doall() {
    ARGS="$1"
    echo Start Group:
    command 0.2 $ARGS &
    command 0.4 $ARGS &
    command 0.6 $ARGS &
    command 0.8 $ARGS &
    wait
}

doall "1 101 stnerf-taekwondo-regularization-none"
