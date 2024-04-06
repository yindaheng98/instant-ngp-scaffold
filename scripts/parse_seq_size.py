import argparse
import json
import numpy as np
import zlib
from scipy import sparse
from parse_seq2bson import (
    load_save, load_params,
    compute_diff_params
)

parser = argparse.ArgumentParser()
parser.add_argument("--start", type=int, required=True, help="The start frame number.")
parser.add_argument("--end", type=int, required=True, help="The end frame number.")
parser.add_argument("--saveformat", type=str, required=True, help="The path format of the saved snapshot.")
parser.add_argument("--fullexportformat", type=str, default=None, help="The path format of exported full video frames (.json).")
parser.add_argument("--intraexportformat", type=str, default=None, help="The path format of exported intra-frame video frames (.json).")
parser.add_argument("--interexportformat", type=str, default=None, help="The path format of exported inter-frame video frames (.json).")
parser.add_argument("-T", type=float, required=True, help="Threshold for set zero in inter frames.")
parser.add_argument("-L", type=float, help="Set this value to use dynamic threshold. Then the threshold will be len(param)*L th largest value in parameters.")

def compute_intra_params(params, last_params, T, L = None):
    diff_params = compute_diff_params(params, last_params, T, L)
    params = np.copy(params)
    params[diff_params==0] = 0
    return params

def get_size(data):
    data_compressed = zlib.compress(data.tobytes())
    data_csr = sparse.csr_matrix(data)
    data_csr_compressed = zlib.compress(data_csr.data.tobytes())
    return len(data_compressed), len(data_csr_compressed)

def export_data(data, path):
    with open(path, "w", encoding="utf8") as f:
        json.dump(data, f, indent=2)

def print_data(perfix, params_size, params_csr_size):
    print(perfix, 
          "params", params_size / 1024 / 1024, "MB",
          "params_csr", params_csr_size / 1024 / 1024, "MB",)

if __name__ == "__main__":
    import os
    args = parser.parse_args()
    root = os.getcwd()
    savepath = os.path.join(root, args.saveformat % args.start)

    sizes = []
    save = load_save(savepath)
    params, _ = load_params(save)
    if args.fullexportformat:
        os.makedirs(os.path.dirname(args.fullexportformat), exist_ok=True)
        params_size, params_csr_size = get_size(params)
        print_data(f"{args.T}  full", params_size, params_csr_size)
        export_data(dict(
            params_size=params_size,
            params_csr_size=params_csr_size,
        ), args.fullexportformat % args.start)
    last_diff_params = np.copy(params)
    last_intr_params = np.copy(params)
    for i in range(args.start + 1, args.end + 1):
        print("do", i-args.start, "/", args.end-args.start)
        savepath = os.path.join(root, args.saveformat % i)
        save = load_save(savepath)
        params, _ = load_params(save)
        if args.fullexportformat:
            os.makedirs(os.path.dirname(args.fullexportformat), exist_ok=True)
            params_size, params_csr_size = get_size(params)
            print_data(f"{args.T} {args.L}  full", params_size, params_csr_size)
            export_data(dict(
                params_size=params_size,
                params_csr_size=params_csr_size,
            ), args.fullexportformat % i)

        if args.intraexportformat:
            os.makedirs(os.path.dirname(args.intraexportformat), exist_ok=True)
            intra_params = compute_intra_params(params, last_diff_params, args.T)
            intra_params_size, intra_params_csr_size = get_size(intra_params)
            print_data(f"{args.T} {args.L} intra:", intra_params_size, intra_params_csr_size)
            export_data(dict(
                intra_params_size=intra_params_size,
                intra_params_csr_size=intra_params_csr_size,
            ), args.intraexportformat % {'i':i, "T": args.T, "L": args.L})

        if args.interexportformat:
            os.makedirs(os.path.dirname(args.interexportformat), exist_ok=True)
            diff_params = compute_diff_params(params, last_diff_params, args.T, args.L)
            last_diff_params += diff_params
            
            diff_params_size, diff_params_csr_size = get_size(diff_params)
            print_data(f"{args.T} {args.L}  diff:", diff_params_size, diff_params_csr_size)
            export_data(dict(
                diff_params_size=diff_params_size,
                diff_params_csr_size=diff_params_csr_size,
            ), args.interexportformat % {'i':i, "T": args.T, "L": args.L})
