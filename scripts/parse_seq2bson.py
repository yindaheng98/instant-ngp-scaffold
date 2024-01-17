import argparse
import bson
import numpy as np
import struct
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument("--start", type=int, required=True, help="The start frame number.")
parser.add_argument("--end", type=int, required=True, help="The end frame number.")
parser.add_argument("--saveformat", type=str, required=True, help="The path format of the saved snapshot.")
parser.add_argument("--intraexportformat", type=str, required=True, help="The path format of exported intra-frame video frames (.bson).")
parser.add_argument("--interexportformat", type=str, required=True, help="The path format of exported inter-frame video frames (.bson).")
parser.add_argument("--interdiffexportformat", type=str, required=True, help="The path format of exported inter-frame video frames (.bson).")

def load_save(path):
    with open(path, "rb") as f:
        return bson.decode_all(f.read())[0]
    
def load_params(save):
    snapshot = save['snapshot']
    params_bin = snapshot['params_binary']
    params_type = snapshot['params_type']
    density_grid_bin = snapshot['density_grid_binary']
    if params_type == "__half":
        return np.frombuffer(params_bin, dtype=np.float16), np.frombuffer(density_grid_bin, dtype=np.float16)
    else:
        return np.frombuffer(params_bin, dtype=np.float32).astype(np.float16), np.frombuffer(density_grid_bin, dtype=np.float16)

T = 1e-6

if __name__ == "__main__":
    import os
    args = parser.parse_args()
    root = os.getcwd()
    os.makedirs(os.path.dirname(args.interexportformat), exist_ok=True)
    os.makedirs(os.path.dirname(args.intraexportformat), exist_ok=True)
    savepath = os.path.join(root, args.saveformat % args.start)
    save = load_save(savepath)
    params, density_grid = load_params(save)
    with open(args.intraexportformat % args.start, "wb") as f:
        f.write(bson.encode({
            "params_size": params.shape[0],
            "density_grid_size": density_grid.shape[0],
            "params": params.tobytes(),
            "density_grid": density_grid.tobytes(),
        }))
    for i in tqdm(range(args.start + 1, args.end + 1)):
        savepath = os.path.join(root, args.saveformat % i)
        save = load_save(savepath)
        last_params, last_density_grid, (params, density_grid) = params, density_grid, load_params(save)
        with open(args.intraexportformat % i, "wb") as f:
            f.write(bson.encode({
                "params_size": params.shape[0],
                "density_grid_size": density_grid.shape[0],
                "params": params.tobytes(),
                "density_grid": density_grid.tobytes(),
            }))
        diff_params = params - last_params
        diff_density_grid = density_grid - last_density_grid
        diff_params_idx = np.where(diff_params > T)[0]
        diff_density_grid_idx = np.where(diff_density_grid > T)[0]
        with open(args.interdiffexportformat % i, "wb") as f:
            f.write(bson.encode({
                "params_size": diff_params_idx.shape[0],
                "density_grid_size": diff_density_grid_idx.shape[0],
                "params": diff_params[diff_params_idx].tobytes(),
                "density_grid": diff_density_grid[diff_density_grid_idx].tobytes(),
                "params_idx": struct.pack(f"{diff_params_idx.shape[0]}L", *diff_params_idx),
                "density_grid_idx": struct.pack(f"{diff_density_grid_idx.shape[0]}L", *diff_density_grid_idx),
            }))
        params_fp32, density_grid_fp32 = params.astype(np.float32), density_grid.astype(np.float32)
        params_fp32[diff_params_idx] += diff_params[diff_params_idx]
        density_grid_fp32[diff_density_grid_idx] += diff_density_grid[diff_density_grid_idx]
        params, density_grid = params_fp32.astype(np.float16), density_grid_fp32.astype(np.float16)
        with open(args.interexportformat % i, "wb") as f:
            f.write(bson.encode({
                "params_size": diff_params_idx.shape[0],
                "density_grid_size": diff_density_grid_idx.shape[0],
                "params": params[diff_params_idx].tobytes(),
                "density_grid": density_grid[diff_density_grid_idx].tobytes(),
                "params_idx": struct.pack(f"{diff_params_idx.shape[0]}L", *diff_params_idx),
                "density_grid_idx": struct.pack(f"{diff_density_grid_idx.shape[0]}L", *diff_density_grid_idx),
            }))
