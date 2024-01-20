import argparse
import json
import numpy as np
import zlib
from scipy import sparse
from parse_seq2bson import load_save, load_params, compute_diff_params, compute_diff_density_grid

parser = argparse.ArgumentParser()
parser.add_argument("--start", type=int, required=True, help="The start frame number.")
parser.add_argument("--end", type=int, required=True, help="The end frame number.")
parser.add_argument("--saveformat", type=str, required=True, help="The path format of the saved snapshot.")
parser.add_argument("--intraexportformat", type=str, required=True, help="The path format of exported intra-frame video frames (.bson).")
parser.add_argument("--interexportformat", type=str, required=True, help="The path format of exported inter-frame video frames (.bson).")
parser.add_argument("-T", type=float, required=True, help="Threshold for set zero in inter frames.")

def get_size(data):
    data_compressed = zlib.compress(data.tobytes())
    data_csr = sparse.csr_matrix(data)
    data_csr_compressed = zlib.compress(data_csr.data.tobytes())
    return len(data_compressed), len(data_csr_compressed)

def export_data(data, path):
    with open(path, "w", encoding="utf8") as f:
        json.dump(data, f, indent=2)

def print_data(params_size, params_csr_size, density_grid_size, density_grid_csr_size):
    print("params", params_size / 1024 / 1024, "MB",
          "params_csr", params_csr_size / 1024 / 1024, "MB",
          "density_grid", density_grid_size / 1024 / 1024, "MB",
          "density_grid_csr", density_grid_csr_size / 1024 / 1024, "MB",)

if __name__ == "__main__":
    import os
    args = parser.parse_args()
    root = os.getcwd()
    os.makedirs(os.path.dirname(args.interexportformat), exist_ok=True)
    os.makedirs(os.path.dirname(args.intraexportformat), exist_ok=True)
    savepath = os.path.join(root, args.saveformat % args.start)

    sizes = []
    save = load_save(savepath)
    params, density_grid = load_params(save)
    params_size, params_csr_size = get_size(params)
    density_grid_size, density_grid_csr_size = get_size(density_grid)
    print_data(params_size, params_csr_size, density_grid_size, density_grid_csr_size)
    export_data(dict(
        params_size=params_size,
        params_csr_size=params_csr_size,
        density_grid_size=density_grid_size,
        density_grid_csr_size=density_grid_csr_size,
    ), args.intraexportformat % args.start)
    last_diff_params, last_diff_density_grid = np.copy(params), np.copy(density_grid)
    last_intr_params, last_intr_density_grid = np.copy(params), np.copy(density_grid)
    for i in range(args.start + 1, args.end + 1):
        print("do", i-args.start, "/", args.end-args.start)
        savepath = os.path.join(root, args.saveformat % i)
        save = load_save(savepath)
        params, density_grid = load_params(save)
        params_size, params_csr_size = get_size(params)
        density_grid_size, density_grid_csr_size = get_size(density_grid)
        print_data(params_size, params_csr_size, density_grid_size, density_grid_csr_size)
        export_data(dict(
            params_size=params_size,
            params_csr_size=params_csr_size,
            density_grid_size=density_grid_size,
            density_grid_csr_size=density_grid_csr_size,
        ), args.intraexportformat % i)

        diff_params = compute_diff_params(params, last_diff_params, args.T)
        diff_density_grid = compute_diff_density_grid(density_grid, last_diff_density_grid, args.T)
        last_diff_params += diff_params
        last_diff_density_grid += diff_density_grid
        
        diff_params_size, diff_params_csr_size = get_size(diff_params)
        diff_density_grid_size, diff_density_grid_csr_size = get_size(diff_density_grid)
        print("diff:")
        print_data(diff_params_size, diff_params_csr_size, diff_density_grid_size, diff_density_grid_csr_size)
        export_data(dict(
            diff_params_size=diff_params_size,
            diff_params_csr_size=diff_params_csr_size,
            diff_density_grid_size=diff_density_grid_size,
            diff_density_grid_csr_size=diff_density_grid_csr_size,
        ), args.interexportformat % {'i':i, "T": args.T})
