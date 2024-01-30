import numpy as np
import matplotlib.pyplot as plt
poses_arr = np.load("data/nerf/coffee_martini/poses_bounds.npy")
poses = poses_arr[:, :-2].reshape([-1, 3, 5]).transpose([1,2,0])
bds = poses_arr[:, -2:].transpose([1,0])
poses = np.concatenate([poses[:, 1:2, :], -poses[:, 0:1, :], poses[:, 2:, :]], 1)
poses = np.moveaxis(poses, -1, 0).astype(np.float32)
bds = np.moveaxis(bds, -1, 0).astype(np.float32)

def normalize(x):
    return x / np.linalg.norm(x)

def viewmatrix(z, up, pos):
    vec2 = normalize(z)
    vec1_avg = up
    vec0 = normalize(np.cross(vec1_avg, vec2))
    vec1 = normalize(np.cross(vec2, vec0))
    m = np.stack([vec0, vec1, vec2, pos], 1)
    return m

def poses_avg(poses):

    hwf = poses[0, :3, -1:]

    center = poses[:, :3, 3].mean(0)
    vec2 = normalize(poses[:, :3, 2].sum(0))
    up = poses[:, :3, 1].sum(0)
    c2w = np.concatenate([viewmatrix(vec2, up, center), hwf], 1)
    
    return c2w

def recenter_poses(poses):

    poses_ = poses+0
    bottom = np.reshape([0,0,0,1.], [1,4])
    c2w = poses_avg(poses)
    c2w = np.concatenate([c2w[:3,:4], bottom], -2)
    bottom = np.tile(np.reshape(bottom, [1,1,4]), [poses.shape[0],1,1])
    poses = np.concatenate([poses[:,:3,:4], bottom], -2)

    poses = np.linalg.inv(c2w) @ poses
    poses_[:,:3,:4] = poses[:,:3,:4]
    poses = poses_
    return poses

poses = recenter_poses(poses)
c2w = poses[:, :3, :4]
hwf = poses[:, :3, 4]

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

pos = c2w[:, :, 3]
pos = pos - pos.mean(axis=0)
scale = (pos.max(axis=0) - pos.min(axis=0)).max()
pos = pos / scale * 2
pos[:, 2] += 1
c2w[:, :, 3] = pos

h, w, f = hwf[:, 0], hwf[:, 1], hwf[:, 2]
K = np.zeros_like(c2w, shape=(c2w.shape[0], 3, 3))
K[:, 2, 2] = 1
K[:, 0, 0] = f
K[:, 1, 1] = f
K[:, 0, 2] = 0.5*w
K[:, 1, 2] = 0.5*h

fig = plt.figure(figsize=(12, 6))
ax = fig.add_subplot(projection='3d')
det = np.linalg.det(c2w[:, :, :3])
print(det)
draw_cameras(ax, c2w, color="tab:blue")
ax.view_init(elev=-90, azim=90, roll=180)
ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)
ax.set_zlim(-1, 1)
plt.show()