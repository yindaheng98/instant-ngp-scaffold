command0() {
    mkdir -p results/grayscale
    ./build/instant-ngp-train \
        --step=$3 \
        --save_snapshot results/grayscale/$2-frame0.bson \
        data/nerf/$1/grayscale/frame1
}

command0 taekwondo stnerf-taekwondo 30000 1
