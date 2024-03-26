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

def load_params_bitfield(save):
    params, density_grid = load_params(save)
    snapshot = save['snapshot']
    density_grid_bitfield = snapshot['density_grid_bitfield']
    return params, density_grid, density_grid_bitfield

def dump_save(path, save, params, density_grid):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    params_bin = params.tobytes()
    density_grid_bin = density_grid.tobytes()
    save['snapshot']['params_binary'] = params_bin
    save['snapshot']['density_grid_binary'] = density_grid_bin
    with open(path, "wb") as f:
        f.write(bson.encode(save))

T_TOOBIG = 65500

def compute_diff_params(params, last_diff_params):
    diff_params = params - last_diff_params
    return diff_params

if __name__ == "__main__":
    import os
    args = parser.parse_args()
    root = os.getcwd()
    savepath = os.path.join(root, args.saveformat % args.start)
    save = load_save(savepath)
    params, density_grid, bitfield = load_params_bitfield(save)
    if args.intraexportformat:
        os.makedirs(os.path.dirname(args.intraexportformat % args.start), exist_ok=True)
        with open(args.intraexportformat % args.start, "wb") as f:
            f.write(zlib.compress(bson.encode({
                "params_size": params.shape[0],
                "density_grid_size": density_grid.shape[0],
                "params": params.tobytes(),
                "density_grid": density_grid.tobytes(),
                "density_grid_bitfield": bitfield,
                "density_grid_bitfield_size": len(bitfield),
            })))
    last_diff_params = np.copy(params)
    last_intr_params = np.copy(params)
    for i in range(args.start + 1, args.end + 1):
        print("do", i-args.start, "/", args.end-args.start)
        savepath = os.path.join(root, args.saveformat % i)
        save = load_save(savepath)
        params, density_grid, bitfield = load_params_bitfield(save)
        if args.intraexportformat:
            os.makedirs(os.path.dirname(args.intraexportformat % i), exist_ok=True)
            with open(args.intraexportformat % i, "wb") as f:
                f.write(zlib.compress(bson.encode({
                    "params_size": params.shape[0],
                    "density_grid_size": density_grid.shape[0],
                    "params": params.tobytes(),
                    "density_grid": density_grid.tobytes(),
                    "density_grid_bitfield": bitfield,
                    "density_grid_bitfield_size": len(bitfield),
                })))

        if not args.interexportformat:
            continue

        density_grid_filtered = np.copy(density_grid)
        density_grid_filtered[density_grid_filtered > 1] = 1
        diff_params = compute_diff_params(params, last_diff_params)
        os.makedirs(os.path.dirname(args.interexportformat % i), exist_ok=True)
        with open(args.interexportformat % i, "wb") as f:
            f.write(zlib.compress(bson.encode({
                "params_size": diff_params.shape[0],
                "density_grid_size": density_grid.shape[0],
                "params": diff_params.tobytes(),
                "density_grid": density_grid_filtered.tobytes(),
                "density_grid_bitfield": bitfield,
                "density_grid_bitfield_size": len(bitfield),
            })))
        last_diff_params += diff_params
        if args.snapshotsimulate_interexportformat:
            dump_save(args.snapshotsimulate_interexportformat % i,
                    save, last_diff_params, density_grid_filtered)

        error_params = params.astype(np.float32) - last_diff_params.astype(np.float32)
        print("error of params", error_params.max(), error_params.min())

        pass
