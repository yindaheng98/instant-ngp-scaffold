import os
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--exec", type=str, required=True, help="path to the ffmpeg")
parser.add_argument("--path", type=str, required=True, help="path to the video folder")
parser.add_argument("--maxt", type=int, default=4, help="max num of thread")
parser.add_argument("--fmt", type=str, default=r"cam[0-9][0-9].mp4", help="re format of mp4 file")

if __name__ == "__main__":
    args = parser.parse_args()
    root = args.path
    t = args.maxt
    for entry in os.scandir(root):
        if not re.match(args.fmt, entry.name):
            continue
        folder = os.path.splitext(entry.name)[0]
        imgs_dir = os.path.join(root, folder)
        os.makedirs(imgs_dir, exist_ok=True)
        cmd = f"{args.exec} -i {entry.path} {imgs_dir}/%03d.png &"
        print(cmd)
        t -= 1
        if t <= 0:
            print("wait")
            t = args.maxt
    print("wait")
