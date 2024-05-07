import argparse
import bson
import numpy as np
from sklearn.cluster import KMeans
import os

parser = argparse.ArgumentParser()
parser.add_argument("--src", type=str, required=True, help="The source bson.")
parser.add_argument("--dst", type=str, required=True, help="The destination bson.")
parser.add_argument("--log2-clusters", type=int, required=True, help="Qualtize from which layer.")
parser.add_argument("--from-layer", type=int, default=0, help="Qualtize from which layer.")

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
    return params


def dump_save(path, save, params):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    params_bin = params.tobytes()
    save['snapshot']['params_binary'] = params_bin
    with open(path, "wb") as f:
        f.write(bson.encode(save))


if __name__ == "__main__":
    import os
    args = parser.parse_args()
    save = load_save(args.src)
    params = load_params(save)
    params_vector = params[OFFSET0:].reshape(-1, N_FEATURES_PER_LEVEL)
    kmeans = KMeans(n_clusters=2**args.log2_clusters, random_state=0, n_init="auto").fit(params_vector)
    compressed_vector = kmeans.predict(params_vector)
    print(save)
