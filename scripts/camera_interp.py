import argparse
import json
import numpy as np
parser = argparse.ArgumentParser()
parser.add_argument("--path", type=str, required=True)
parser.add_argument("--pathto", type=str, required=True)
parser.add_argument("--times", type=int, required=True)
parser.add_argument("--start", type=int, required=True)
parser.add_argument("--end", type=int, required=True)

if __name__ == "__main__":
    import os
    args = parser.parse_args()
    root = os.getcwd()
    path = os.path.join(root, args.path)
    pathto = os.path.join(root, args.pathto)
    frame = 0
    keyframes = []
    with open(path, "r") as f:
        keyframes = [json.loads(line) for line in f.readlines()]
    with open(pathto, "w", encoding="utf8") as f:
        f.write(json.dumps(keyframes[0]))
        f.write("\n")
        for i in range(1, len(keyframes)):
            last_frame = keyframes[i-1]
            this_frame = keyframes[i]
            last_matrix = np.matrix(last_frame["camera"]["matrix"])
            this_matrix = np.matrix(this_frame["camera"]["matrix"])
            for i in range(1, args.times + 1):
                matrix = (last_matrix - this_matrix) / args.times * i + last_matrix
                last_frame["camera"]["matrix"] = matrix.tolist()
                last_frame["frame"] = frame + args.start
                f.write(json.dumps(last_frame))
                f.write("\n")
                frame = (frame + 1) % (args.end - args.start)
    print(keyframes)
