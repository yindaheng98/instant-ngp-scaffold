mkdir -p results/grayscale
train_color() {
    ./build/instant-ngp-train \
        --step=$3 \
        --save_snapshot results/grayscale/$2-color-frame1-$4.bson \
        -c configs/nerf/$4.json \
        data/nerf/$1/frame1
}
render_color() {
    mkdir -p results/grayscale/$2-color-frame1-$4
    ./build/instant-ngp-viewer \
        --load_snapshot results/grayscale/$2-color-frame1-$4.bson \
        --savecam camera/$2-$5.txt \
        --save_image results/grayscale/$2-color-frame1-$4/camera-$5/%d.bin \
        data/nerf/$1/frame1
}
convert_color() {
    python scripts/grayscale/bin2image.py \
        --format results/grayscale/$2-color-frame1-$4/camera-$5/%d.bin
}
train_gray() {
    ./build/instant-ngp-train \
        --step=$3 \
        --save_snapshot results/grayscale/$2-gray-frame1-$4.bson \
        -c configs/nerf/$4.json \
        data/nerf/$1/grayscale/frame1
}
render_gray() {
    mkdir -p results/grayscale/$2-gray-frame1-$4
    ./build/instant-ngp-viewer \
        --load_snapshot results/grayscale/$2-gray-frame1-$4.bson \
        --savecam camera/$2-$5.txt \
        --save_image results/grayscale/$2-gray-frame1-$4/camera-$5/%d.bin \
        data/nerf/$1/frame1
}
convert_gray() {
    python scripts/grayscale/bin2image.py \
        --format results/grayscale/$2-gray-frame1-$4/camera-$5/%d.bin
}
train_both() {
    train_color $1 $2 $3 $4
    train_gray $1 $2 $3 $4
}
eval_both() {
    render_color $1 $2 $3 $4 $5
    convert_color $1 $2 $3 $4 $5
    rm results/grayscale/$2-color-frame1-$4/camera-$5/*.bin
    render_gray $1 $2 $3 $4 $5
    convert_gray $1 $2 $3 $4 $5
    rm results/grayscale/$2-gray-frame1-$4/camera-$5/*.bin
}
train_all() {
    train_both $1 $2 $3 base
    train_both $1 $2 $3 base_18
    train_both $1 $2 $3 base_18_3
    train_both $1 $2 $3 base_18_2
    train_both $1 $2 $3 base_18_1
    train_both $1 $2 $3 base_17
    train_both $1 $2 $3 base_17_3
    train_both $1 $2 $3 base_17_2
    train_both $1 $2 $3 base_17_1
    train_both $1 $2 $3 base_16
    train_both $1 $2 $3 base_16_3
    train_both $1 $2 $3 base_16_2
    train_both $1 $2 $3 base_16_1
    train_both $1 $2 $3 base_15
    train_both $1 $2 $3 base_15_3
    train_both $1 $2 $3 base_15_2
    train_both $1 $2 $3 base_15_1
    train_both $1 $2 $3 base_14
    train_both $1 $2 $3 base_14_3
    train_both $1 $2 $3 base_14_2
    train_both $1 $2 $3 base_14_1
}
eval_all() {
    eval_both $1 $2 $3 base $4
    eval_both $1 $2 $3 base_17 $4
    eval_both $1 $2 $3 base_17_3 $4
    eval_both $1 $2 $3 base_17_2 $4
    eval_both $1 $2 $3 base_17_1 $4
    eval_both $1 $2 $3 base_16 $4
    eval_both $1 $2 $3 base_16_3 $4
    eval_both $1 $2 $3 base_16_2 $4
    eval_both $1 $2 $3 base_16_1 $4
    eval_both $1 $2 $3 base_15 $4
    eval_both $1 $2 $3 base_15_3 $4
    eval_both $1 $2 $3 base_15_2 $4
    eval_both $1 $2 $3 base_15_1 $4
    eval_both $1 $2 $3 base_14 $4
    eval_both $1 $2 $3 base_14_3 $4
    eval_both $1 $2 $3 base_14_2 $4
    eval_both $1 $2 $3 base_14_1 $4
}

train_all taekwondo stnerf-taekwondo 30000
eval_all taekwondo stnerf-taekwondo 30000 1
eval_all taekwondo stnerf-taekwondo 30000 2
eval_all taekwondo stnerf-taekwondo 30000 3
eval_all taekwondo stnerf-taekwondo 30000 4

train_all walking stnerf-walking 30000 1
eval_all walking stnerf-walking 30000 1
eval_all walking stnerf-walking 30000 2
eval_all walking stnerf-walking 30000 3
eval_all walking stnerf-walking 30000 4

train_all coffee_martini coffee_martini 30000 1
eval_all coffee_martini coffee_martini 30000 1
eval_all coffee_martini coffee_martini 30000 2
eval_all coffee_martini coffee_martini 30000 3
eval_all coffee_martini coffee_martini 30000 4

train_all flame_steak flame_steak 30000 1
eval_all flame_steak flame_steak 30000 1
eval_all flame_steak flame_steak 30000 2
eval_all flame_steak flame_steak 30000 3
eval_all flame_steak flame_steak 30000 4

train_all sear_steak sear_steak 30000 1
eval_all sear_steak sear_steak 30000 1
eval_all sear_steak sear_steak 30000 2
eval_all sear_steak sear_steak 30000 3
eval_all sear_steak sear_steak 30000 4

train_all discussion discussion 30000 1
eval_all discussion discussion 30000 1
eval_all discussion discussion 30000 2
eval_all discussion discussion 30000 3
eval_all discussion discussion 30000 4

train_all stepin stepin 30000 1
eval_all stepin stepin 30000 1
eval_all stepin stepin 30000 2
eval_all stepin stepin 30000 3
eval_all stepin stepin 30000 4

train_all trimming trimming 30000 1
eval_all trimming trimming 30000 1
eval_all trimming trimming 30000 2
eval_all trimming trimming 30000 3
eval_all trimming trimming 30000 4

train_all vrheadset vrheadset 30000 1
eval_all vrheadset vrheadset 30000 1
eval_all vrheadset vrheadset 30000 2
eval_all vrheadset vrheadset 30000 3
eval_all vrheadset vrheadset 30000 4
