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
command taekwondo stnerf-taekwondo "1e-5" 30000 10000 1 101
command taekwondo stnerf-taekwondo "1e-6" 30000 10000 1 101

command walking stnerf-walking "1e-4" 30000 10000 1 75
command walking stnerf-walking "1e-5" 30000 10000 1 75
command walking stnerf-walking "1e-6" 30000 10000 1 75

command coffee_martini coffee_martini "1e-4" 30000 10000 1 300
command coffee_martini coffee_martini "1e-5" 30000 10000 1 300
command coffee_martini coffee_martini "1e-6" 30000 10000 1 300

command flame_steak flame_steak "1e-4" 30000 10000 1 300
command flame_steak flame_steak "1e-5" 30000 10000 1 300
command flame_steak flame_steak "1e-6" 30000 10000 1 300

command sear_steak sear_steak "1e-4" 30000 10000 1 300
command sear_steak sear_steak "1e-5" 30000 10000 1 300
command sear_steak sear_steak "1e-6" 30000 10000 1 300
