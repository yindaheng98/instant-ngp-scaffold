mkdir -p results/vq
# train_color taekwondo stnerf-taekwondo 300 base # debug
render_color() {
    mkdir -p results/$3/color/kmeans-none
    ./build/instant-ngp-replay \
        --start $1 --end $2 \
        --load_snapshot results/$3/frame1.bson \
        --init results/$3/intra/frame1.bson \
        --frameformat results/$3/intra/frame%d.bson \
        --savecam $4 \
        --save_image results/$3/color/kmeans-none/%d.bin
}
render_color 2 100 coffee_martini-regularization-1e-7 camera/coffee_martini-1.txt # debug
