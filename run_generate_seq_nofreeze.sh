#!/bin/bash
command() {
    echo $1 $2 start
    python3 /volume/scripts/parse_seq2bson.py --start 1 --end 101 \
        --saveformat results/stnerf-taekwondo/frame%d-nofreeze.bson \
        --intraexportformat results/stnerf-taekwondo/frame%d-nofreeze-intra.bson \
        --interexportformat results/stnerf-taekwondo/frame%\(i\)d-nofreezeT=%\(T\)fT_density=%\(T_density\)f-inter.bson \
        --snapshotsimulate_interexportformat results/stnerf-taekwondo/frame%\(i\)d-nofreezeT=%\(T\)fT_density=%\(T_density\)f-snapshotsimulate.bson \
        --T $1 --T_density $2
    echo $1 $2 complete
}

echo Start Group:
# 1 0.5 0.1 0.05 0.01
command 1 1 &

command 0.5 0.5 &

command 0.1 0.1 &

command 0.05 0.05 &

command 0.01 0.01 &
wait
