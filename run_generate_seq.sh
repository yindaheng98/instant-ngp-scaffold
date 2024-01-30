#!/bin/bash
command() {
    echo $1 $2 start
    python3 /volume/scripts/parse_seq2bson.py --start 1 --end 101 \
        --saveformat results/stnerf-taekwondo/frame%d.bson \
        --intraexportformat results/stnerf-taekwondo/frame%d-intra.bson \
        --interexportformat results/stnerf-taekwondo/frame%\(i\)dT=%\(T\)fT_density=%\(T_density\)f-inter.bson \
        --snapshotsimulate_interexportformat results/stnerf-taekwondo/frame%\(i\)dT=%\(T\)fT_density=%\(T_density\)f-snapshotsimulate.bson \
        --T $1 --T_density $2
    echo $1 $2 complete
}

echo Start Group:
# 1 0.5 0.1 0.05 0.01
command 1 1 &

command 1 0.1 &

command 0.5 0.1 &
command 0.4 0.1 &
command 0.3 0.1 &
command 0.2 0.1 &
command 0.1 0.1 &

# command 0.5 0.05 &

# command 0.05 0.1 &
# command 0.1 0.05 &
command 0.05 0.05 &

# command 0.01 0.1 &
command 0.1 0.01 &
command 0.01 0.01 &
wait
