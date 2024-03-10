command0() {
    ./instant-ngp-train \
        --step=$3 \
        --save_snapshot results/$2-frame0.bson \
        data/nerf/$1/img/$4
}
command() {
    mkdir -p results/$2-regularization-$3
    cp results/$2-frame0.bson results/$2-regularization-$3/frame$6.bson
    python scripts/train_seq.py \
        --init_steps $4 --steps $5 --start $6 --end $7 \
        --trainargs=--decay=0.5 \
        --trainargs=--encreg=$3 \
        --initformat "data/nerf/$1/img/%d" \
        --dataformat "data/nerf/$1/img/%d" \
        --saveformat "results/$2-regularization-$3/frame%d.bson" \
        --executable "./instant-ngp-train"
}
command1() {
    mkdir -p results/$2-regularization-none
    cp results/$2-frame0.bson results/$2-regularization-none/frame$6.bson
    python scripts/train_seq.py \
        --init_steps $4 --steps $5 --start $6 --end $7 \
        --trainargs=--decay=0.5 \
        --initformat "data/nerf/$1/img/%d" \
        --dataformat "data/nerf/$1/img/%d" \
        --saveformat "results/$2-regularization-none/frame%d.bson" \
        --executable "./instant-ngp-train"
}


command0 basketball basketball 30000 0
command1 basketball basketball "none" 30000 10000 0 194
command basketball basketball "1e-4" 30000 10000 0 194
command basketball basketball "1e-5" 30000 10000 0 194
command basketball basketball "1e-6" 30000 10000 0 194
command basketball basketball "1e-7" 30000 10000 0 194

command0 sport_1 sport_1 30000 0
command1 sport_1 sport_1 "none" 30000 10000 0 200
command sport_1 sport_1 "1e-4" 30000 10000 0 200
command sport_1 sport_1 "1e-5" 30000 10000 0 200
command sport_1 sport_1 "1e-6" 30000 10000 0 200
command sport_1 sport_1 "1e-7" 30000 10000 0 200

command0 sport_2 sport_2 30000 0
command1 sport_2 sport_2 "none" 30000 10000 0 200
command sport_2 sport_2 "1e-4" 30000 10000 0 200
command sport_2 sport_2 "1e-5" 30000 10000 0 200
command sport_2 sport_2 "1e-6" 30000 10000 0 200
command sport_2 sport_2 "1e-7" 30000 10000 0 200

command0 sport_3 sport_3 30000 0
command1 sport_3 sport_3 "none" 30000 10000 0 200
command sport_3 sport_3 "1e-4" 30000 10000 0 200
command sport_3 sport_3 "1e-5" 30000 10000 0 200
command sport_3 sport_3 "1e-6" 30000 10000 0 200
command sport_3 sport_3 "1e-7" 30000 10000 0 200
