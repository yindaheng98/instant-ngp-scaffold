#!/bin/bash
python3 /volume/scripts/parse_seq2bson.py --start 1 --end 101 \
    --saveformat results/stnerf-taekwondo/frame%d.bson \
    --intraexportformat results/stnerf-taekwondo/frame%d-intra.bson \
    --interexportformat results/stnerf-taekwondo/frame%\(i\)dT=%\(T\)fT_density=%\(T_density\)f-inter.bson \
    --snapshotsimulate_interexportformat results/stnerf-taekwondo/frame%\(i\)dT=%\(T\)fT_density=%\(T_density\)f-snapshotsimulate.bson \
    --T 0.5 --T_density 0.5
