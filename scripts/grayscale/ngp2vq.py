import argparse
import bson
import numpy as np
from sklearn.cluster import KMeans
import os
import pickle

parser = argparse.ArgumentParser()
parser.add_argument("--src", type=str, required=True, help="The source bson.")
parser.add_argument("--dst", type=str, required=True, help="The destination bson.")
parser.add_argument("--log2-clusters", type=int, required=True, help="Qualtize from which layer.")
parser.add_argument("--from-layer", type=int, default=0, help="Qualtize from which layer.")
parser.add_argument("--save-kmeans", type=str, default=None, help="Save kmeans cluster centers.")
parser.add_argument("--overwrite", action="store_true", help="Overwrite saved kmeans cluster centers.")

OFFSET0 = 10240
N_FEATURES_PER_LEVEL = 4
OFFSET_TABLE = [0, 4096, 89280, 613568, 1137856, 1662144, 2186432, 2710720, 3235008]


def load_save(path):
    with open(path, "rb") as f:
        return bson.decode_all(f.read())[0]


def load_params(save):
    snapshot = save['snapshot']
    params_bin = snapshot['params_binary']
    params_type = snapshot['params_type']
    if params_type == "__half":
        params = np.frombuffer(params_bin, dtype=np.float16)
    else:
        params = np.frombuffer(params_bin, dtype=np.float32).astype(np.float16)
    return np.copy(params)


def dump_save(path, save, params):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    params_bin = params.astype(np.float16).tobytes()
    save['snapshot']['params_binary'] = params_bin
    with open(path, "wb") as f:
        f.write(bson.encode(save))


if __name__ == "__main__":
    import os
    args = parser.parse_args()
    print(args.src, "->", args.dst)
    save = load_save(args.src)
    params = load_params(save)
    params_vector = params[OFFSET0:].reshape(-1, N_FEATURES_PER_LEVEL)

    kmeans = None
    if args.save_kmeans and os.path.isfile(args.save_kmeans) and not args.overwrite:
        try:
            with open(args.save_kmeans, "rb") as f:
                kmeans = pickle.load(f)
        except Exception as e:
            print("!Overwrite:", e)
    if kmeans is None:
        kmeans = KMeans(n_clusters=2**args.log2_clusters, random_state=0, n_init="auto")
        kmeans.fit(params_vector)
        if args.save_kmeans:
            with open(args.save_kmeans, "wb") as f:
                pickle.dump(kmeans, f)
    quantized_vector = kmeans.predict(params_vector)
    dequantized_vector = kmeans.cluster_centers_[quantized_vector]
    params[OFFSET0:] = dequantized_vector.reshape(-1).astype(np.float16)
    dump_save(args.dst, save, params)
