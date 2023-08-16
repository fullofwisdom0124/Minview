import numpy as np

array = np.full((8192*6144), 128, dtype=np.uint16)

array.tofile("test.raw")