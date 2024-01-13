import argparse
import bson
import numpy as np
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument("--start", type=int, required=True, help="The start frame number.")
parser.add_argument("--end", type=int, required=True, help="The end frame number.")
parser.add_argument("--saveformat", type=str, required=True, help="The path format of the saved snapshot.")
parser.add_argument("--exportformat", type=str, required=True, help="The path format of exported video file (.npz).")

def load_save(path):
    with open(path, "rb") as f:
        return bson.decode_all(f.read())[0]
    
def load_params(save):
    snapshot = save['snapshot']
    params_bin = snapshot['params_binary']
    params_type = snapshot['params_type']
    if params_type == "__half":
        return np.frombuffer(params_bin, dtype=np.float16).astype(np.float32)
    else:
        return np.frombuffer(params_bin, dtype=np.float32)

if __name__ == "__main__":
    import os
    args = parser.parse_args()
    root = os.getcwd()
    os.makedirs(os.path.dirname(args.exportformat), exist_ok=True)
    savepath = os.path.join(root, args.saveformat % args.start)
    save = load_save(savepath)
    params = load_params(save)
    np.savez_compressed(args.exportformat % args.start, arr_0=params)
    for i in tqdm(range(args.start + 1, args.end + 1)):
        savepath = os.path.join(root, args.saveformat % i)
        save = load_save(savepath)
        last_params, params = params, load_params(save)
        np.savez_compressed(args.exportformat % i, arr_0=params)

