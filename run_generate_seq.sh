#!/bin/bash
command0() {
    echo $1 $2 $3 $4 $5 start
    python ./scripts/parse_seq2bson.py --start $3 --end $4 \
        --saveformat results/$5/frame%d.bson \
        --intraexportformat results/$5/intra/frame%d.bson
    echo $1 $2 $3 $4 $5 complete
}

command_destroy() {
    echo $1 $2 $3 $4 $5 start
    python ./scripts/parse_seq2bson_destroyed.py --start $3 --end $4 \
        --saveformat results/$5/frame%d.bson \
        --exportformat results/$5/fp16destroy/frame%d.bson
    python ./scripts/parse_seq2bson_no_simulation.py --start $3 --end $4 \
        --saveformat results/$5/frame%d.bson \
        --exportformat results/$5/nosimulationdestroy/T=%\(T\)fT_density=%\(T_density\)f/frame%\(i\)d.bson \
        --T $1 --T_density $2
    echo $1 $2 $3 $4 $5 complete
}

command() {
    echo $1 $2 $3 $4 $5 start
    python ./scripts/parse_seq2bson.py --start $3 --end $4 \
        --saveformat results/$5/frame%d.bson \
        --interexportformat results/$5/inter/T=%\(T\)fT_density=%\(T_density\)f/frame%\(i\)d.bson \
        --snapshotsimulate_interexportformat results/$5/inter/T=%\(T\)fT_density=%\(T_density\)f/frame%\(i\)d-snapshotsimulate.bson \
        --T $1 --T_density $2
    echo $1 $2 $3 $4 $5 complete
}

doall() {
    echo Start Group:
    # 1 0.5 0.1 0.05 0.01
    ARGS=$1
    command0 0 0 $ARGS &
    command_destroy 0.1 0.1 $ARGS &
    # command 1 1 $ARGS &

    # command 1 0.1 $ARGS &

    command 0.5 0.1 $ARGS &
    command 0.4 0.1 $ARGS &
    command 0.3 0.1 $ARGS &
    command 0.2 0.1 $ARGS &
    command 0.1 0.1 $ARGS &

    # command 0.5 0.05 &

    # command 0.05 0.1 &
    # command 0.1 0.05 &
    # command 0.05 0.05 $ARGS &

    # command 0.01 0.1 &
    # command 0.1 0.01 $ARGS &
    # command 0.01 0.01 $ARGS &
    wait
}

doall "1 101 stnerf-taekwondo"
doall "1 75 stnerf-walking"
doall "1 100 coffee_martini"
doall "1 100 flame_steak"
doall "1 100 sear_steak"
