import argparse
import bson
import numpy as np
import zlib

parser = argparse.ArgumentParser()
parser.add_argument("--start", type=int, required=True, help="The start frame number.")
parser.add_argument("--end", type=int, required=True, help="The end frame number.")
parser.add_argument("--saveformat", type=str, required=True, help="The path format of the saved snapshot.")
parser.add_argument("--intraexportformat", type=str, required=True, help="The path format of exported intra-frame video frames (.bson).")
parser.add_argument("--interexportformat", type=str, required=True, help="The path format of exported inter-frame video frames (.bson).")
parser.add_argument("-T", type=float, required=True, help="Threshold for set zero in inter frames.")

def load_save(path):
    with open(path, "rb") as f:
        return bson.decode_all(f.read())[0]

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

    if np.isposinf(params).any():
        replace = params[~np.isposinf(params)].max()
        print("+inf in params, replace by", replace)
        params[np.isposinf(params)] = replace
    if np.isneginf(params).any():
        replace = params[~np.isneginf(params)].min()
        print("-inf in params, replace by", replace)
        params[np.isneginf(params)] = replace

    if np.isposinf(density_grid).any():
        replace = density_grid[~np.isposinf(density_grid)].max()
        print("+inf in density_grid, replace by", replace)
        density_grid[np.isposinf(density_grid)] = replace
    if np.isneginf(density_grid).any():
        replace = density_grid[~np.isneginf(density_grid)].min()
        print("-inf in density_grid, replace by", replace)
        density_grid[np.isneginf(density_grid)] = replace

    return params, density_grid

T_TOOBIG = 65500

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
        f.write(zlib.compress(bson.encode({
            "params_size": params.shape[0],
            "density_grid_size": density_grid.shape[0],
            "params": params.tobytes(),
            "density_grid": density_grid.tobytes(),
        })))
    last_diff_params, last_diff_density_grid = np.copy(params), np.copy(density_grid)
    last_intr_params, last_intr_density_grid = np.copy(params), np.copy(density_grid)
    for i in range(args.start + 1, args.end + 1):
        print("do", i-args.start, "/", args.end-args.start)
        savepath = os.path.join(root, args.saveformat % i)
        save = load_save(savepath)
        params, density_grid = load_params(save)
        with open(args.intraexportformat % i, "wb") as f:
            f.write(zlib.compress(bson.encode({
                "params_size": params.shape[0],
                "density_grid_size": density_grid.shape[0],
                "params": params.tobytes(),
                "density_grid": density_grid.tobytes(),
            })))

        diff_density_grid_fp32 = density_grid.astype(np.float32) - last_diff_density_grid.astype(np.float32)
        diff_density_grid_rel = diff_density_grid_fp32 / last_diff_density_grid.astype(np.float32)
        diff_density_grid_rel[np.isnan(diff_density_grid_rel)] = diff_density_grid_fp32[np.isnan(diff_density_grid_rel)]
        density_grid_fp32 = last_diff_density_grid.astype(np.float32) + diff_density_grid_fp32
        density_grid_error_for_compare = density_grid - (last_diff_density_grid + diff_density_grid_fp32.astype(np.float16))

        diff_params = params - last_diff_params
        diff_density_grid = density_grid - last_diff_density_grid
        diff_params[np.abs(diff_params) <= args.T] = 0
        diff_density_grid[np.abs(diff_density_grid) <= args.T] = 0
        diff_density_grid[diff_density_grid_fp32 > T_TOOBIG] = T_TOOBIG
        diff_density_grid[diff_density_grid_fp32 < -T_TOOBIG] = -T_TOOBIG
        diff_density_grid[density_grid_fp32 > T_TOOBIG] = (T_TOOBIG - last_diff_density_grid)[density_grid_fp32 > T_TOOBIG]
        diff_density_grid[density_grid_fp32 < -T_TOOBIG] = (-T_TOOBIG - last_diff_density_grid)[density_grid_fp32 < -T_TOOBIG]
        with open(args.interexportformat % {'i':i, "T": args.T}, "wb") as f:
            f.write(zlib.compress(bson.encode({
                "params_size": diff_params.shape[0],
                "density_grid_size": diff_density_grid.shape[0],
                "params": diff_params.tobytes(),
                "density_grid": diff_density_grid.tobytes(),
            })))
        last_diff_params += diff_params
        last_diff_density_grid += diff_density_grid

        error_params = params.astype(np.float32) - last_diff_params.astype(np.float32)
        error_density_grid = density_grid.astype(np.float32) - last_diff_density_grid.astype(np.float32)
        print("error of params", error_params.max(), error_params.min())
        print("error of density_grid", error_density_grid.max(), error_density_grid.min())
        cause_of_max_error_idx = error_density_grid == error_density_grid.max()
        cause_of_min_error_idx = error_density_grid == error_density_grid.min()
        print("cause of density_grid error",
              error_density_grid.max(),
              "error should be",
              density_grid_error_for_compare[cause_of_max_error_idx],
              density_grid[cause_of_max_error_idx],
              last_diff_density_grid[cause_of_max_error_idx],
              diff_density_grid[cause_of_max_error_idx])
        print("cause of density_grid error",
              error_density_grid.min(),
              "error should be",
              density_grid_error_for_compare[cause_of_min_error_idx],
              density_grid[cause_of_min_error_idx],
              last_diff_density_grid[cause_of_min_error_idx],
              diff_density_grid[cause_of_min_error_idx])

        pass
