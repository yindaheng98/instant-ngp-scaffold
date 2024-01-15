import os
import numpy as np
import matplotlib.pyplot as plt

# https://github.com/DarlingHang/st-nerf/blob/e0c1c32b09d90101218410443193ddabc1f66d2f/data/datasets/utils.py#L6


def campose_to_extrinsic(camposes):
    if camposes.shape[1] != 12:
        raise Exception(" wrong campose data structure!")

    res = np.zeros((camposes.shape[0], 4, 4))

    res[:, 0, :] = camposes[:, 0:4]
    res[:, 1, :] = camposes[:, 4:8]
    res[:, 2, :] = camposes[:, 8:12]
    res[:, 3, 3] = 1.0

    return res


# https://github.com/DarlingHang/st-nerf/blob/e0c1c32b09d90101218410443193ddabc1f66d2f/data/datasets/utils.py#L20
def read_intrinsics(fn_instrinsic):
    fo = open(fn_instrinsic)
    data = fo.readlines()
    i = 0
    Ks = []
    while i < len(data):
        tmp = data[i].split()
        a = [float(i) for i in tmp[0:3]]
        a = np.array(a)
        b = [float(i) for i in tmp[3:6]]
        b = np.array(b)
        c = [float(i) for i in tmp[6:9]]
        c = np.array(c)
        res = np.vstack([a, b, c])
        Ks.append(res)

        i = i+1
    Ks = np.stack(Ks)
    fo.close()

    return Ks

VIDEO_FOLDER = 'data/nerf/taekwondo'
# https://github.com/DarlingHang/st-nerf/blob/e0c1c32b09d90101218410443193ddabc1f66d2f/data/datasets/frame_dataset.py#L25C23-L25C23
camposes = np.loadtxt(os.path.join(VIDEO_FOLDER, 'pose', 'RT_c2w.txt'))
Ts = campose_to_extrinsic(camposes)
Ks = read_intrinsics(os.path.join(VIDEO_FOLDER, 'pose', 'K.txt'))
stnerf = Ts[:, :3, :]
pos = stnerf[:, :, 3]
pos = pos - pos.mean(axis=0)
scale = (pos.max(axis=0) - pos.min(axis=0)).max()
pos = pos / scale * 2
pos[:, 2] += 1
stnerf[:, :, 3] = pos

def draw_cameras(ax, extrinsic, color):
    poses = extrinsic[:, :, 3]
    ax.scatter(xs=poses[:, 0], ys=poses[:, 1], zs=poses[:, 2], s=3, c=color)
    rotas = extrinsic[:, :, :3]
    for i, (pose, rota) in enumerate(zip(poses, rotas)):
        ax.text(pose[0], pose[1], pose[2], str(i))
        for r, c in zip(rota.T, ['r', 'g', 'b']):
            r_to = pose + r
            ax.plot(xs=[pose[0], r_to[0]],
                    ys=[pose[1], r_to[1]],
                    zs=[pose[2], r_to[2]], c=c, linewidth=1)


fig = plt.figure(figsize=(12, 6))
ax = fig.add_subplot(projection='3d')
draw_cameras(ax, stnerf, color="tab:blue")
ax.view_init(elev=-90, azim=90, roll=180)
ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)
ax.set_zlim(-1, 1)
plt.show()
