command() {
    python scripts/train_seq.py \
        --init_steps $4 --steps $5 --start $6 --end $7 \
        --trainargs=--decay=0.5 \
        --trainargs=--encreg=$3 \
        --initformat "data/nerf/$1/frame%d" \
        --dataformat "data/nerf/$1/frame%d" \
        --saveformat "results/$2-regularization-$3/frame%d.bson" \
        --executable "./instant-ngp-train"
}

command taekwondo stnerf-taekwondo "1e-4" 30000 10000 1 101
