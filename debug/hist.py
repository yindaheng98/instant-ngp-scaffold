import os
import glob
import collections
import numpy as np
import cv2
import matplotlib.pyplot as plt
root = "data/nerf/walking/residuals"
frame_folder = os.path.join(root, "frame20")
hist = np.zeros(256, dtype=np.int64)
for frame_file in glob.glob(os.path.join(frame_folder, "*.png")):
    frame = cv2.imread(frame_file)
    for i, count in collections.Counter(frame.reshape((-1))).items():
        hist[i] += count
print(hist)
fig = plt.figure(figsize=(12, 3))
ax = fig.subplots(nrows=1, ncols=1)
ax.plot(range(len(hist)), hist)
plt.show()