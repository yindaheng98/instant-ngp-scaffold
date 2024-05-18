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
# render_color 2 100 coffee_martini-regularization-1e-7 coffee_martini-1 # debug
convert_color() {
    python scripts/grayscale/bin2image.py \
        --format results/$1/color/kmeans-none/$2/%d.bin
}
convert_color coffee_martini-regularization-1e-7 coffee_martini-1 # debug
