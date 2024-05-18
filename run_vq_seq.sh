mkdir -p results/vq
# train_color taekwondo stnerf-taekwondo 300 base # debug
render_color() {
    mkdir -p results/$3/color/kmeans-none
    ./build/instant-ngp-replay \
        --start $1 --end $2 \
        --load_snapshot results/$3/frame1.bson \
        --init results/$3/intra/frame1.bson \
        --frameformat results/$3/intra/frame%d.bson \
        --savecam camera/$4.txt \
        --save_image results/$3/color/kmeans-none/$4/%d.bin
}
# render_color 2 100 coffee_martini-regularization-none coffee_martini-1 # debug
convert_color() {
    python scripts/grayscale/bin2image.py \
        --format results/$1/color/kmeans-none/$2/%d.bin
}
# convert_color coffee_martini-regularization-none coffee_martini-1 # debug
vq_color() {
    mkdir -p results/$3/color/kmeans-$4/models/intra
    python scripts/grayscale/ngp2vq_intra.py \
        --src results/$3/intra/frame1.bson \
        --dst results/$3/color/kmeans-$4/models/intra/frame1.bson \
        --save-kmeans results/$3/color/kmeans-$4/kmeans-params.pkl \
        --log2-clusters $4 \
        --overwrite
    for i in $(seq $1 $2); do
        python scripts/grayscale/ngp2vq_intra.py \
            --src results/$3/intra/frame$i.bson \
            --dst results/$3/color/kmeans-$4/models/intra/frame$i.bson \
            --log2-clusters $4
        # --save-kmeans results/$3/color/kmeans-$4/kmeans-params.pkl
    done
}
# vq_color 2 100 coffee_martini-regularization-none 6
render_vq_color() {
    mkdir -p results/$3/color/kmeans-$4
    ./build/instant-ngp-replay \
        --start $1 --end $2 \
        --load_snapshot results/$3/frame1.bson \
        --init results/$3/color/kmeans-$4/models/intra/frame1.bson \
        --frameformat results/$3/color/kmeans-$4/models/intra/frame%d.bson \
        --savecam camera/$5.txt \
        --save_image results/$3/color/kmeans-$4/$5/%d.bin
}
# render_vq_color 2 100 coffee_martini-regularization-none 6 coffee_martini-1 # debug
convert_vq_color() {
    python scripts/grayscale/bin2image.py \
        --format results/$1/color/kmeans-$2/$3/%d.bin
}
# convert_vq_color coffee_martini-regularization-none 6 coffee_martini-1 # debug
train_gray() {
    mkdir -p results/$2-regularization-none-gray
    if [ -e "results/$2-frame0-gray.bson" ]; then
        ./build/instant-ngp-train \
            --step=$3 \
            --save_snapshot results/$2-frame0-gray.bson \
            data/nerf/$1/grayscale/frame$4
    fi
    cp results/$2-frame0.bson results/$2-regularization-none-gray/frame$6.bson
    python scripts/train_seq.py \
        --init_steps $4 --steps $5 --start $6 --end $7 \
        --trainargs=--decay=0.5 \
        --initformat "data/nerf/$1/grayscale/frame%d" \
        --dataformat "data/nerf/$1/grayscale/frame%d" \
        --saveformat "results/$2-regularization-none-gray/frame%d.bson" \
        --executable "./build/instant-ngp-train"
}
# train_gray coffee_martini coffee_martini "none" 30000 10000 1 101
gray2bson() {
    python ./scripts/parse_seq2bson.py --start $1 --end $2 \
        --saveformat results/$3-regularization-none-gray/frame%d.bson \
        --fullexportformat results/$3-regularization-none-gray/intra/frame%d.bson
}
# gray2bson 1 101 coffee_martini
render_gray_color() {
    mkdir -p results/$3-regularization-none-gray/color/kmeans-none
    ./build/instant-ngp-replay \
        --start $1 --end $2 \
        --load_snapshot results/$3-regularization-none-gray/frame1.bson \
        --init results/$3-regularization-none-gray/intra/frame1.bson \
        --frameformat results/$3-regularization-none-gray/intra/frame%d.bson \
        --savecam camera/$4.txt \
        --save_image results/$3-regularization-none-gray/color/kmeans-none/$4/%d.bin
}
render_gray_color 2 100 coffee_martini coffee_martini-1 # debug
