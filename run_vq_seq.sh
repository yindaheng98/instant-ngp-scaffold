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
            --log2-clusters $4 \
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
convert_vq_color coffee_martini-regularization-none 6 coffee_martini-1 # debug
