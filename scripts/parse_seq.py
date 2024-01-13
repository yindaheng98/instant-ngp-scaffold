import argparse
import bson
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("--start", type=int, required=True, help="The start frame number.")
parser.add_argument("--end", type=int, required=True, help="The end frame number.")
parser.add_argument("--saveformat", type=str, required=True, help="The path format of the saved snapshot.")

def load_save(path):
    with open(path, "rb") as f:
        return bson.decode_all(f.read())[0]
    
def load_params(save):
    snapshot = save['snapshot']
    params_bin = snapshot['params_binary']
    params_type = snapshot['params_type']
    if params_type == "__half":
        return np.frombuffer(params_bin, dtype=np.float16)
    else:
        return np.frombuffer(params_bin, dtype=np.float32)

if __name__ == "__main__":
    import os
    args = parser.parse_args()
    root = os.getcwd()
    savepath = os.path.join(root, args.saveformat % args.start)
    os.makedirs(os.path.dirname(savepath), exist_ok=True)
    save = load_save(savepath)
    params = load_params(save)
    for i in range(args.start + 1, args.end + 1):
        savepath = os.path.join(root, args.saveformat % i)
        save = load_save(savepath)
        last_params, params = params, load_params(save)
        params_diff = params - last_params
        print(last_params, params)
