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
command 0.5 &
command 0.1 &
command 0.05 &
command 0.01 &
wait
