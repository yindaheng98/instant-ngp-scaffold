train_color() {
    ./build/instant-ngp-train \
        --step=$3 \
        --save_snapshot results/grayscale/$2-color-frame0-$4.bson \
        -c configs/nerf/$4.json \
        data/nerf/$1/frame1
}
mkdir -p results/grayscale
train_grayscale() {
    ./build/instant-ngp-train \
        --step=$3 \
        --save_snapshot results/grayscale/$2-grayscale-frame0-$4.bson \
        -c configs/nerf/$4.json \
        data/nerf/$1/grayscale/frame1
}

train_color taekwondo stnerf-taekwondo 30000 base
train_color taekwondo stnerf-taekwondo 30000 base_14
train_color taekwondo stnerf-taekwondo 30000 base_15
train_color taekwondo stnerf-taekwondo 30000 base_16
train_color taekwondo stnerf-taekwondo 30000 base_17
train_grayscale taekwondo stnerf-taekwondo 30000 base
train_grayscale taekwondo stnerf-taekwondo 30000 base_14
train_grayscale taekwondo stnerf-taekwondo 30000 base_15
train_grayscale taekwondo stnerf-taekwondo 30000 base_16
train_grayscale taekwondo stnerf-taekwondo 30000 base_17
