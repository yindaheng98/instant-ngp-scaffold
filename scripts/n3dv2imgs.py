import os
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--exec", type=str, required=True, help="path to the ffmpeg")
parser.add_argument("--path", type=str, required=True, help="path to the video folder")

if __name__ == "__main__":
    args = parser.parse_args()
    root = args.path
    for entry in os.scandir(root):
        if not re.match(r"cam[0-9][0-9].mp4", entry.name):
            continue
        folder = os.path.splitext(entry.name)[0]
        imgs_dir = os.path.join(root, folder)
        os.makedirs(imgs_dir, exist_ok=True)
        cmd = f"{args.exec} -i {entry.path} {imgs_dir}/%03d.png &"
        print(cmd)
    print("wait")
