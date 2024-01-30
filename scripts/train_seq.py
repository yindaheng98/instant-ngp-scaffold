import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--start", type=int, required=True, help="The start frame number.")
parser.add_argument("--end", type=int, required=True, help="The end frame number.")
parser.add_argument("--dataformat", type=str, required=True, help="The path format of the frames data.")
parser.add_argument("--saveformat", type=str, required=True, help="The path format of the snapshot to save.")
parser.add_argument("--executable", type=str, required=True, help="The path to the trainer executable.")
parser.add_argument("--init_steps", type=int, required=True, help="How many steps do you want to train in init model.")
parser.add_argument("--steps", type=int, required=True, help="How many steps do you want to train.")
parser.add_argument("--no_freeze", action="store_true", help="Do not freeze.")

if __name__ == "__main__":
    import os
    import subprocess
    args = parser.parse_args()
    root = os.getcwd()
    datapath = os.path.join(root, args.dataformat % args.start)
    savepath = os.path.join(root, args.saveformat % args.start)
    executable = os.path.join(root, args.executable)
    os.makedirs(os.path.dirname(savepath), exist_ok=True)
    cmd = [executable, f"--step={args.init_steps}", f"--save_snapshot={savepath}", datapath]
    print(cmd)
    if not os.path.exists(savepath):
        subprocess.run(cmd)
    for i in range(args.start + 1, args.end + 1):
        last_savepath = savepath
        datapath = os.path.join(root, args.dataformat % i)
        savepath = os.path.join(root, args.saveformat % i)
        cmd = [executable, f"--step={args.steps}", f"--save_snapshot={savepath}", f"--snapshot={last_savepath}", datapath]
        if not args.no_freeze:
            cmd += ["--freeze"]
        print(cmd)
        if not os.path.exists(savepath):
            subprocess.run(cmd)
