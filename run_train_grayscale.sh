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
train_grayscale() {
    ./build/instant-ngp-train \
        --step=$3 \
        --save_snapshot results/grayscale/$2-grayscale-frame1-$4.bson \
        -c configs/nerf/$4.json \
        data/nerf/$1/grayscale/frame1
}
command() {
    train_color $1 $2 $3 $4
    render_color $1 $2 $3 $4 $5
    convert_color $1 $2 $3 $4 $5
    rm results/grayscale/$2-color-frame1-$4/camera-$5/*.bin
}

command taekwondo stnerf-taekwondo 300 base 1
