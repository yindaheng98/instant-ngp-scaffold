#!/bin/bash
command0() {
    echo $1  $2 $3 $4 start
    python ./scripts/parse_seq2bson.py --start $2 --end $3 \
        --saveformat results/$4/frame%d.bson \
        --fullexportformat results/$4/intra/frame%d.bson
    echo $1 $2 $3 $4 complete
}

command1() {
    echo $1  $2 $3 $4 start
    python ./scripts/parse_seq2bson.py --start $2 --end $3 \
        --saveformat results/$4/frame%d.bson \
        --interexportformat results/$4/inter/T=%\(T\)fL=%\(L\)s/frame%\(i\)d.bson \
        --snapshotsimulate_interexportformat results/$4/inter/T=%\(T\)fL=%\(L\)s/frame%\(i\)d-snapshotsimulate.bson \
        -T 0.01 -L $1
    echo $1 $2 $3 $4 complete
}

doall() {
    echo Start Group:
    # 1 0.5 0.1 0.05 0.01
    ARGS=$1
    command0 0.0 $ARGS &
    command1 0.2 $ARGS &
    command1 0.4 $ARGS &
    command1 0.6 $ARGS &
    command1 0.8 $ARGS &
    command1 1.0 $ARGS &
    wait
}

doall "1 101 stnerf-taekwondo-regularization-1e-6"
doall "1 101 stnerf-taekwondo-regularization-1e-7"
doall "1 75 stnerf-walking-regularization-1e-6"
doall "1 75 stnerf-walking-regularization-1e-7"
doall "1 100 coffee_martini-regularization-1e-6"
doall "1 100 coffee_martini-regularization-1e-7"
doall "1 100 flame_steak-regularization-1e-6"
doall "1 100 flame_steak-regularization-1e-7"
doall "1 100 sear_steak-regularization-1e-6"
doall "1 100 sear_steak-regularization-1e-7"
