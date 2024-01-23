import argparse
import numpy as np
from parse_seq2bson import parser, load_save, dump_save

parser = argparse.ArgumentParser()
parser.add_argument("--start", type=int, required=True, help="The start frame number.")
parser.add_argument("--end", type=int, required=True, help="The end frame number.")
parser.add_argument("--saveformat", type=str, required=True, help="The path format of the saved snapshot.")
parser.add_argument("--exportformat", type=str, required=True, help="The path format of exported intra-frame video frames (.bson).")

def load_params(save):
    snapshot = save['snapshot']
    params_bin = snapshot['params_binary']
    params_type = snapshot['params_type']
    density_grid_bin = snapshot['density_grid_binary']
    if params_type == "__half":
        params, density_grid = np.frombuffer(params_bin, dtype=np.float16), np.frombuffer(density_grid_bin, dtype=np.float16)
    else:
        params, density_grid = np.frombuffer(params_bin, dtype=np.float32).astype(np.float16), np.frombuffer(density_grid_bin, dtype=np.float16)
    if np.isnan(params).any():
        raise ValueError("params has NaN!")
    if np.isnan(density_grid).any():
        raise ValueError("density_grid has NaN!")

    params, density_grid = np.copy(params), np.copy(density_grid)
    return params, density_grid

if __name__ == "__main__":
    import os
    args = parser.parse_args()
    root = os.getcwd()
    os.makedirs(os.path.dirname(args.exportformat), exist_ok=True)
    savepath = os.path.join(root, args.saveformat % args.start)
    save = load_save(savepath)
    params, density_grid = load_params(save)
    last_diff_params, last_diff_density_grid = np.copy(params), np.copy(density_grid)
    last_intr_params, last_intr_density_grid = np.copy(params), np.copy(density_grid)
    for i in range(args.start + 1, args.end + 1):
        print("do", i-args.start, "/", args.end-args.start)
        savepath = os.path.join(root, args.saveformat % i)
        save = load_save(savepath)
        params, density_grid = load_params(save)
        diff_params = params - last_diff_params
        diff_density_grid = density_grid - last_diff_density_grid
        last_diff_params += diff_params
        last_diff_density_grid += diff_density_grid
        dump_save(args.exportformat % i,
                  save, last_diff_params, last_diff_density_grid)

        print(last_diff_params[np.isnan(last_diff_params)].shape)
        print(last_diff_density_grid[np.isnan(last_diff_density_grid)].shape)
        pass
