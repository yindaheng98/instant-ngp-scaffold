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
command() {
    train_color $1 $2 $3 $4
    render_color $1 $2 $3 $4 $5
    convert_color $1 $2 $3 $4 $5
    rm results/grayscale/$2-color-frame1-$4/camera-$5/*.bin
    train_gray $1 $2 $3 $4
    render_gray $1 $2 $3 $4 $5
    convert_gray $1 $2 $3 $4 $5
    rm results/grayscale/$2-gray-frame1-$4/camera-$5/*.bin
}
command_all() {
    command $1 $2 $3 base $4
    command $1 $2 $3 base_17 $4
    command $1 $2 $3 base_17_3 $4
    command $1 $2 $3 base_17_2 $4
    command $1 $2 $3 base_17_1 $4
    command $1 $2 $3 base_16 $4
    command $1 $2 $3 base_16_3 $4
    command $1 $2 $3 base_16_2 $4
    command $1 $2 $3 base_16_1 $4
    command $1 $2 $3 base_15 $4
    command $1 $2 $3 base_15_3 $4
    command $1 $2 $3 base_15_2 $4
    command $1 $2 $3 base_15_1 $4
    command $1 $2 $3 base_14 $4
    command $1 $2 $3 base_14_3 $4
    command $1 $2 $3 base_14_2 $4
    command $1 $2 $3 base_14_1 $4
}

command_all taekwondo stnerf-taekwondo 30000 1
command_all taekwondo stnerf-taekwondo 30000 2
command_all taekwondo stnerf-taekwondo 30000 3
command_all taekwondo stnerf-taekwondo 30000 4
command_all walking stnerf-walking 30000 1
command_all walking stnerf-walking 30000 2
command_all walking stnerf-walking 30000 3
command_all walking stnerf-walking 30000 4
command_all coffee_martini coffee_martini 30000 1
command_all coffee_martini coffee_martini 30000 2
command_all coffee_martini coffee_martini 30000 3
command_all coffee_martini coffee_martini 30000 4
command_all flame_steak flame_steak 30000 1
command_all flame_steak flame_steak 30000 2
command_all flame_steak flame_steak 30000 3
command_all flame_steak flame_steak 30000 4
command_all sear_steak sear_steak 30000 1
command_all sear_steak sear_steak 30000 2
command_all sear_steak sear_steak 30000 3
command_all sear_steak sear_steak 30000 4
command_all discussion discussion 30000 1
command_all discussion discussion 30000 2
command_all discussion discussion 30000 3
command_all discussion discussion 30000 4
command_all stepin stepin 30000 1
command_all stepin stepin 30000 2
command_all stepin stepin 30000 3
command_all stepin stepin 30000 4
command_all trimming trimming 30000 1
command_all trimming trimming 30000 2
command_all trimming trimming 30000 3
command_all trimming trimming 30000 4
command_all vrheadset vrheadset 30000 1
command_all vrheadset vrheadset 30000 2
command_all vrheadset vrheadset 30000 3
command_all vrheadset vrheadset 30000 4
