#!/bin/bash
command() {
    echo $1 start
    python3 /volume/scripts/parse_seq2csr.py \
        --start 1 --end 101 \
        --saveformat results/stnerf-taekwondo/frame%d.bson \
        --intraexportformat results/stnerf-taekwondo/frame%d-intra.json \
        --interexportformat results/stnerf-taekwondo/frame%\(i\)dT=%\(T\)f-inter.json \
        -T $1
    echo $1 complete
}

echo Start Group:
command 1 &
command 0.9 &
command 0.8 &
command 0.7 &
command 0.6 &
command 0.5 &
command 0.4 &
command 0.3 &
command 0.2 &
command 0.1 &
command 0.05 &
command 0.01 &
wait
