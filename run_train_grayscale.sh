mkdir -p results/grayscale
train_color() {
    ./build/instant-ngp-train \
        --step=$3 \
        --save_snapshot results/grayscale/$2-color-frame1-$4.bson \
        -c configs/nerf/$4.json \
        data/nerf/$1/frame1
}
# train_color taekwondo stnerf-taekwondo 300 base # debug
render_color() {
    mkdir -p results/grayscale/$2-color-frame1-$4
    ./build/instant-ngp-viewer \
        --load_snapshot results/grayscale/$2-color-frame1-$4.bson \
        --savecam camera/$2-$5.txt \
        --save_image results/grayscale/$2-color-frame1-$4/camera-$5/%d.bin \
        data/nerf/$1/frame1
}
# render_color taekwondo stnerf-taekwondo '' base 1 # debug
convert_color() {
    python scripts/grayscale/bin2image.py \
        --format results/grayscale/$2-color-frame1-$4/camera-$5/%d.bin
}
# convert_color '' stnerf-taekwondo '' base 1 # debug
vq_color() {
    python scripts/grayscale/ngp2vq.py \
    --src results/grayscale/$1-color-frame1-$2.bson \
    --dst results/grayscale/$1-color-frame1-$2-vq-exp$3.bson \
    --save-kmeans results/grayscale/$1-color-frame1-$2-kmeans-exp$3.pkl \
    --log2-clusters $3 \
    --overwrite
}
# vq_color stnerf-taekwondo base 8 # debug
render_vq_color() {
    mkdir -p results/grayscale/$2-color-frame1-$4
    ./build/instant-ngp-viewer \
        --load_snapshot results/grayscale/$2-color-frame1-$4-vq-exp$6.bson \
        --savecam camera/$2-$5.txt \
        --save_image results/grayscale/$2-color-frame1-$4/kmeans-$6/camera-$5/%d.bin \
        data/nerf/$1/frame1
}
# render_vq_color taekwondo stnerf-taekwondo '' base 1 8 # debug
convert_vq_color() {
    python scripts/grayscale/bin2image.py \
        --format results/grayscale/$2-color-frame1-$4/kmeans-$6/camera-$5/%d.bin
}
# convert_vq_color '' stnerf-taekwondo '' base 1 8 # debug
train_gray() {
    ./build/instant-ngp-train \
        --step=$3 \
        --save_snapshot results/grayscale/$2-gray-frame1-$4.bson \
        -c configs/nerf/$4.json \
        data/nerf/$1/grayscale/frame1
}
# train_gray taekwondo stnerf-taekwondo 300 base # debug
render_gray() {
    mkdir -p results/grayscale/$2-gray-frame1-$4
    ./build/instant-ngp-viewer \
        --load_snapshot results/grayscale/$2-gray-frame1-$4.bson \
        --savecam camera/$2-$5.txt \
        --save_image results/grayscale/$2-gray-frame1-$4/camera-$5/%d.bin \
        data/nerf/$1/frame1
}
# render_gray taekwondo stnerf-taekwondo '' base 1 # debug
convert_gray() {
    python scripts/grayscale/bin2image.py \
        --format results/grayscale/$2-gray-frame1-$4/camera-$5/%d.bin
}
# convert_gray '' stnerf-taekwondo '' base 1 # debug
vq_gray() {
    python scripts/grayscale/ngp2vq.py \
    --src results/grayscale/$1-gray-frame1-$2.bson \
    --dst results/grayscale/$1-gray-frame1-$2-vq-exp$3.bson \
    --save-kmeans results/grayscale/$1-gray-frame1-$2-kmeans-exp$3.pkl \
    --log2-clusters $3 \
    --overwrite
}
# vq_gray stnerf-taekwondo base 8 # debug
render_vq_gray() {
    mkdir -p results/grayscale/$2-gray-frame1-$4
    ./build/instant-ngp-viewer \
        --load_snapshot results/grayscale/$2-gray-frame1-$4-vq-exp$6.bson \
        --savecam camera/$2-$5.txt \
        --save_image results/grayscale/$2-gray-frame1-$4/kmeans-$6/camera-$5/%d.bin \
        data/nerf/$1/frame1
}
# render_vq_gray taekwondo stnerf-taekwondo '' base 1 8 # debug
convert_vq_gray() {
    python scripts/grayscale/bin2image.py \
        --format results/grayscale/$2-gray-frame1-$4/kmeans-$6/camera-$5/%d.bin
}
# convert_vq_gray '' stnerf-taekwondo '' base 1 8 # debug

train_both() {
    train_color $1 $2 $3 $4
    train_gray $1 $2 $3 $4
}
# train_both taekwondo stnerf-taekwondo 300 base # debug
eval_both() {
    render_color $1 $2 '' $4 $5
    convert_color '' $2 '' $4 $5
    rm results/grayscale/$2-color-frame1-$4/camera-$5/*.bin
    render_gray $1 $2 '' $4 $5
    convert_gray '' $2 '' $4 $5
    rm results/grayscale/$2-gray-frame1-$4/camera-$5/*.bin
}
# eval_both taekwondo stnerf-taekwondo '' base 1 # debug
vq_both() {
    vq_color $1 $2 $3
    vq_gray $1 $2 $3
}
# vq_both stnerf-taekwondo base 8 # debug
eval_vq() {
    render_vq_color $1 $2 '' $4 $5 $6
    convert_vq_color '' $2 '' $4 $5 $6
    rm results/grayscale/$2-color-frame1-$4/kmeans-$6/camera-$5/*.bin
    render_vq_gray $1 $2 '' $4 $5 $6
    convert_vq_gray '' $2 '' $4 $5 $6
    rm results/grayscale/$2-gray-frame1-$4/kmeans-$6/camera-$5/*.bin
}
# eval_vq taekwondo stnerf-taekwondo '' base 1 8 # debug

train_all() {
    train_both $1 $2 $3 base
    vq_both $2 base 10
    vq_both $2 base 9
    vq_both $2 base 8
    vq_both $2 base 7
    vq_both $2 base 6
}
eval_all() {
    eval_both $1 $2 '' base $3
    eval_vq $1 $2 '' base $3 10
    eval_vq $1 $2 '' base $3 9
    eval_vq $1 $2 '' base $3 8
    eval_vq $1 $2 '' base $3 7
    eval_vq $1 $2 '' base $3 6
}

train_all taekwondo stnerf-taekwondo 30000
eval_all taekwondo stnerf-taekwondo 1
eval_all taekwondo stnerf-taekwondo 2
eval_all taekwondo stnerf-taekwondo 3
eval_all taekwondo stnerf-taekwondo 4

train_all walking stnerf-walking 30000 1
eval_all walking stnerf-walking 1
eval_all walking stnerf-walking 2
eval_all walking stnerf-walking 3
eval_all walking stnerf-walking 4

train_all coffee_martini coffee_martini 30000 1
eval_all coffee_martini coffee_martini 1
eval_all coffee_martini coffee_martini 2
eval_all coffee_martini coffee_martini 3
eval_all coffee_martini coffee_martini 4

train_all flame_steak flame_steak 30000 1
eval_all flame_steak flame_steak 1
eval_all flame_steak flame_steak 2
eval_all flame_steak flame_steak 3
eval_all flame_steak flame_steak 4

train_all sear_steak sear_steak 30000 1
eval_all sear_steak sear_steak 1
eval_all sear_steak sear_steak 2
eval_all sear_steak sear_steak 3
eval_all sear_steak sear_steak 4

train_all discussion discussion 30000 1
eval_all discussion discussion 1
eval_all discussion discussion 2
eval_all discussion discussion 3
eval_all discussion discussion 4

train_all stepin stepin 30000 1
eval_all stepin stepin 1
eval_all stepin stepin 2
eval_all stepin stepin 3
eval_all stepin stepin 4

train_all trimming trimming 30000 1
eval_all trimming trimming 1
eval_all trimming trimming 2
eval_all trimming trimming 3
eval_all trimming trimming 4

train_all vrheadset vrheadset 30000 1
eval_all vrheadset vrheadset 1
eval_all vrheadset vrheadset 2
eval_all vrheadset vrheadset 3
eval_all vrheadset vrheadset 4
