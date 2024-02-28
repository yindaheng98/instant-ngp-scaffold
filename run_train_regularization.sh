command0() {
    ./instant-ngp-train \
        --step=$3 \
        --save_snapshot results/$2-frame0.bson \
        data/nerf/$1/frame$4
}
command() {
    mkdir -p results/$2-regularization-$3
    cp results/$2-frame0.bson results/$2-regularization-$3/frame$6.bson
    python scripts/train_seq.py \
        --init_steps $4 --steps $5 --start $6 --end $7 \
        --trainargs=--decay=0.5 \
        --trainargs=--encreg=$3 \
        --initformat "data/nerf/$1/frame%d" \
        --dataformat "data/nerf/$1/frame%d" \
        --saveformat "results/$2-regularization-$3/frame%d.bson" \
        --executable "./instant-ngp-train"
}
command1() {
    mkdir -p results/$2-regularization-none
    cp results/$2-frame0.bson results/$2-regularization-none/frame$6.bson
    python scripts/train_seq.py \
        --init_steps $4 --steps $5 --start $6 --end $7 \
        --trainargs=--decay=0.5 \
        --initformat "data/nerf/$1/frame%d" \
        --dataformat "data/nerf/$1/frame%d" \
        --saveformat "results/$2-regularization-none/frame%d.bson" \
        --executable "./instant-ngp-train"
}


command0 taekwondo stnerf-taekwondo 30000 1
command1 taekwondo stnerf-taekwondo "none" 30000 10000 1 101
command taekwondo stnerf-taekwondo "1e-4" 30000 10000 1 101
command taekwondo stnerf-taekwondo "1e-5" 30000 10000 1 101
command taekwondo stnerf-taekwondo "1e-6" 30000 10000 1 101

command0 walking stnerf-walking 30000 1
command1 taekwondo stnerf-walking "none" 30000 10000 1 75
command walking stnerf-walking "1e-4" 30000 10000 1 75
command walking stnerf-walking "1e-5" 30000 10000 1 75
command walking stnerf-walking "1e-6" 30000 10000 1 75

command0 coffee_martini coffee_martini 30000 1
command1 coffee_martini coffee_martini "none" 30000 10000 1 300
command coffee_martini coffee_martini "1e-4" 30000 10000 1 300
command coffee_martini coffee_martini "1e-5" 30000 10000 1 300
command coffee_martini coffee_martini "1e-6" 30000 10000 1 300

command0 flame_steak flame_steak 30000 1
command1 flame_steak flame_steak "none" 30000 10000 1 300
command flame_steak flame_steak "1e-4" 30000 10000 1 300
command flame_steak flame_steak "1e-5" 30000 10000 1 300
command flame_steak flame_steak "1e-6" 30000 10000 1 300

command0 sear_steak sear_steak 30000 1
command1 sear_steak sear_steak "none" 30000 10000 1 300
command sear_steak sear_steak "1e-4" 30000 10000 1 300
command sear_steak sear_steak "1e-5" 30000 10000 1 300
command sear_steak sear_steak "1e-6" 30000 10000 1 300
