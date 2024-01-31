import argparse
import numpy as np
from parse_seq2bson import parser, load_save, load_params, dump_save, compute_diff_params, compute_diff_density_grid

parser = argparse.ArgumentParser()
parser.add_argument("--start", type=int, required=True, help="The start frame number.")
parser.add_argument("--end", type=int, required=True, help="The end frame number.")
parser.add_argument("--saveformat", type=str, required=True, help="The path format of the saved snapshot.")
parser.add_argument("--exportformat", type=str, required=True, help="The path format of exported intra-frame video frames (.bson).")
parser.add_argument("--T", type=float, default=0., help="Threshold for set zero in inter frames.")
parser.add_argument("--T_density", type=float, default=0., help="Threshold for set zero in inter frames.")

if __name__ == "__main__":
    import os
    args = parser.parse_args()
    root = os.getcwd()
    os.makedirs(os.path.dirname(args.exportformat), exist_ok=True)
    savepath = os.path.join(root, args.saveformat % args.start)
    save = load_save(savepath)
    params, density_grid = load_params(save)
    last_params, last_density_grid = np.copy(params), np.copy(density_grid)
    last_simulate_params, last_simulate_density_grid = np.copy(params), np.copy(density_grid)
    for i in range(args.start + 1, args.end + 1):
        print("do", i-args.start, "/", args.end-args.start)
        savepath = os.path.join(root, args.saveformat % i)
        save = load_save(savepath)
        params, density_grid = load_params(save)
        diff_params = compute_diff_params(params, last_params, args.T)
        diff_density_grid = compute_diff_density_grid(density_grid, last_density_grid, args.T_density)
        last_simulate_params += diff_params
        last_simulate_density_grid += diff_density_grid
        dump_save(args.exportformat % {'i':i, "T": args.T, "T_density": args.T_density},
                  save, last_simulate_params, last_simulate_density_grid)
        last_params, last_density_grid = params, density_grid
        params_error = params - last_simulate_params
        density_grid_error = density_grid - last_simulate_density_grid
        print("no simulation params_error: ", params_error.min(), params_error.mean(), params_error.max())
        print("no simulation density_grid_error: ", density_grid_error.min(), density_grid_error.mean(), density_grid_error.max())
        pass
