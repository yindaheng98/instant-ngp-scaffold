import bson
import zlib
from parse_seq2bson import load_save

if __name__ == "__main__":
    import os
    root = os.getcwd()
    savepath = 'D:/MyPrograms/instant-ngp-flow/results/stnerf-taekwondo-regularization-none/inter/T=0.100000T_density=0.100000/frame2.bson'
    with open(savepath, "rb") as f:
        save = bson.decode_all(zlib.decompress(f.read()))
        print(save)