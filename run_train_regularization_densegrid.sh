command0() {
    ./instant-ngp-train \
        --step=$3 \
        --save_snapshot results/$2-$5-frame0.bson \
        --config=configs/nerf/$5.json \
        data/nerf/$1/frame$4
}
command() {
    mkdir -p results/$2-regularization-$3-$8
    cp results/$2-$8-frame0.bson results/$2-regularization-$3-$8/frame$6.bson
    python scripts/train_seq.py \
        --init_steps $4 --steps $5 --start $6 --end $7 \
        --trainargs=--decay=0.5 \
        --trainargs=--encreg=$3 \
        --trainargs=--config=configs/nerf/$8.json \
        --initformat "data/nerf/$1/frame%d" \
        --dataformat "data/nerf/$1/frame%d" \
        --saveformat "results/$2-regularization-$3-$8/frame%d.bson" \
        --executable "./instant-ngp-train"
}

command0 taekwondo stnerf-taekwondo 30000 1 densegrid
command taekwondo stnerf-taekwondo "1e-6" 30000 10000 1 101 densegrid
command taekwondo stnerf-taekwondo "1e-6" 30000 10000 1 101 densegrid
command0 taekwondo stnerf-taekwondo 30000 1 densegrid344
command taekwondo stnerf-taekwondo "1e-6" 30000 10000 1 101 densegrid344
command taekwondo stnerf-taekwondo "1e-6" 30000 10000 1 101 densegrid344
