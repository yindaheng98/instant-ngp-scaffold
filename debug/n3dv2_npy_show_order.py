import os
import json
import re
import numpy as np
import matplotlib.pyplot as plt

def load_transform(folder):
    file = os.path.join(folder, "transforms.json")
    with open(file) as f:
        data = json.load(f)
        ls = {}
        for frame in data["frames"]:
            ls[frame["file_path"]] = np.array(frame["transform_matrix"])
        return ls

n3dv2i = load_transform("data/nerf/coffee_martini/frame001")
colmap = load_transform("data/nerf/test")
pass


def draw_cameras(ax, extrinsic):
    for name, e in extrinsic.items():
        rota, pose = e[:, :3], e[:, 3]
        ax.text(pose[0], pose[1], pose[2], re.search(r"cam[0-9][0-9]", name).group())
        for r, c in zip(rota.T, ['r', 'g', 'b']):
            r_to = pose + r
            ax.plot(xs=[pose[0], r_to[0]],
                    ys=[pose[1], r_to[1]],
                    zs=[pose[2], r_to[2]], c=c, linewidth=1)

fig = plt.figure(figsize=(12, 6))
ax = fig.add_subplot(projection='3d')
draw_cameras(ax, n3dv2i)
draw_cameras(ax, colmap)
ax.view_init(elev=-90, azim=90, roll=180)
ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)
ax.set_zlim(-1, 1)
plt.show()