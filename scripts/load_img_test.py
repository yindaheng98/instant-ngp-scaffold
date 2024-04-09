import bson
import zlib
import numpy as np
from parse_seq2bson import load_save
import matplotlib.pyplot as plt

if __name__ == "__main__":
    import os
    root = os.getcwd()
    savepath = "D:\\MyPrograms\\instant-ngp-flow\\results\\stnerf-taekwondo-regularization-1e-7\\gridhit\\M=200000\\img\\31.bin"
    data = np.fromfile(savepath, dtype='float32')
    data = data.reshape((1080,1920,4))
    plt.imshow(data)
    print(data)
    plt.show()