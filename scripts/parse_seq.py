import argparse
import bson

parser = argparse.ArgumentParser()
parser.add_argument("--start", type=int, required=True, help="The start frame number.")
parser.add_argument("--end", type=int, required=True, help="The end frame number.")
parser.add_argument("--saveformat", type=str, required=True, help="The path format of the saved snapshot.")

def load_snapshot(path):
    with open(path, "rb") as f:
        return bson.decode_all(f.read())[0]

if __name__ == "__main__":
    import os
    args = parser.parse_args()
    root = os.getcwd()
    savepath = os.path.join(root, args.saveformat % args.start)
    os.makedirs(os.path.dirname(savepath), exist_ok=True)
    snapshot = load_snapshot(savepath)
    print(snapshot)
