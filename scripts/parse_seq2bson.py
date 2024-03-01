import argparse
import bson
import numpy as np
import zlib
import os

parser = argparse.ArgumentParser()
parser.add_argument("--start", type=int, required=True, help="The start frame number.")
parser.add_argument("--end", type=int, required=True, help="The end frame number.")
parser.add_argument("--saveformat", type=str, required=True, help="The path format of the saved snapshot.")
parser.add_argument("--intraexportformat", type=str, default=None, help="The path format of exported intra-frame video frames (.bson).")
parser.add_argument("--interexportformat", type=str, default=None, help="The path format of exported inter-frame video frames (.bson).")
parser.add_argument("--snapshotsimulate_interexportformat", type=str, default=None, help="The path format of exported inter-frame video frames simulated by intra frames (.bson).")
parser.add_argument("--T", type=float, default=0., help="Threshold for set zero in inter frames.")
parser.add_argument("--T_density", type=float, default=0., help="Threshold for set zero in inter frames.")

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
        print(np.isposinf(density_grid).sum(), "+inf in density_grid, replace by", replace)
        density_grid[np.isposinf(density_grid)] = replace
    if np.isneginf(density_grid).any():
        replace = density_grid[~np.isneginf(density_grid)].min()
        print(np.isneginf(density_grid).sum(), "-inf in density_grid, replace by", replace)
        density_grid[np.isneginf(density_grid)] = replace

    return params, density_grid

def dump_save(path, save, params, density_grid):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    params_bin = params.tobytes()
    density_grid_bin = density_grid.tobytes()
    save['snapshot']['params_binary'] = params_bin
    save['snapshot']['density_grid_binary'] = density_grid_bin
    with open(path, "wb") as f:
        f.write(bson.encode(save))

T_TOOBIG = 65500

def compute_diff_params(params, last_diff_params, T):
    diff_params = params - last_diff_params
    diff_params[np.abs(diff_params) <= T] = 0
    return diff_params

def compute_diff_density_grid(density_grid, last_diff_density_grid, T_density):
    diff_density_grid_fp32 = density_grid.astype(np.float32) - last_diff_density_grid.astype(np.float32)
    diff_density_grid_rel = diff_density_grid_fp32 / last_diff_density_grid.astype(np.float32)
    diff_density_grid_rel[np.isnan(diff_density_grid_rel)] = diff_density_grid_fp32[np.isnan(diff_density_grid_rel)]
    density_grid_fp32 = last_diff_density_grid.astype(np.float32) + diff_density_grid_fp32

    diff_density_grid = density_grid - last_diff_density_grid
    diff_density_grid[np.abs(diff_density_grid) <= T_density] = 0
    diff_density_grid[diff_density_grid_fp32 > T_TOOBIG] = T_TOOBIG
    diff_density_grid[diff_density_grid_fp32 < -T_TOOBIG] = -T_TOOBIG
    diff_density_grid[density_grid_fp32 > T_TOOBIG] = (T_TOOBIG - last_diff_density_grid)[density_grid_fp32 > T_TOOBIG]
    diff_density_grid[density_grid_fp32 < -T_TOOBIG] = (-T_TOOBIG - last_diff_density_grid)[density_grid_fp32 < -T_TOOBIG]
    return diff_density_grid

def compute_intra_params(params, last_params, T):
    diff_params = compute_diff_params(params, last_params, T)
    params = np.copy(params)
    params[diff_params==0] = 0
    return params

def compute_intra_density_grid(density_grid, last_density_grid, T_density):
    diff_density_grid = compute_diff_density_grid(density_grid, last_density_grid, T_density)
    density_grid = np.copy(density_grid)
    density_grid[diff_density_grid==0] = 0
    return density_grid

if __name__ == "__main__":
    import os
    args = parser.parse_args()
    root = os.getcwd()
    savepath = os.path.join(root, args.saveformat % args.start)
    save = load_save(savepath)
    params, density_grid = load_params(save)
    if args.intraexportformat:
        os.makedirs(os.path.dirname(args.intraexportformat % args.start), exist_ok=True)
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
        if args.intraexportformat:
            os.makedirs(os.path.dirname(args.intraexportformat % i), exist_ok=True)
            with open(args.intraexportformat % i, "wb") as f:
                f.write(zlib.compress(bson.encode({
                    "params_size": params.shape[0],
                    "density_grid_size": density_grid.shape[0],
                    "params": params.tobytes(),
                    "density_grid": density_grid.tobytes(),
                })))

        if not args.interexportformat:
            continue
        diff_density_grid_fp32 = density_grid.astype(np.float32) - last_diff_density_grid.astype(np.float32)
        density_grid_error_for_compare = density_grid - (last_diff_density_grid + diff_density_grid_fp32.astype(np.float16))

        diff_params = compute_diff_params(params, last_diff_params, args.T)
        diff_density_grid = compute_diff_density_grid(density_grid, last_diff_density_grid, args.T_density)
        os.makedirs(os.path.dirname(args.interexportformat % {'i':i, "T": args.T, "T_density": args.T_density}), exist_ok=True)
        with open(args.interexportformat % {'i':i, "T": args.T, "T_density": args.T_density}, "wb") as f:
            f.write(zlib.compress(bson.encode({
                "params_size": diff_params.shape[0],
                "density_grid_size": diff_density_grid.shape[0],
                "params": diff_params.tobytes(),
                "density_grid": diff_density_grid.tobytes(),
            })))
        last_diff_params += diff_params
        last_diff_density_grid += diff_density_grid
        if args.snapshotsimulate_interexportformat:
            dump_save(args.snapshotsimulate_interexportformat % {'i':i, "T": args.T, "T_density": args.T_density},
                    save, last_diff_params, last_diff_density_grid)

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
