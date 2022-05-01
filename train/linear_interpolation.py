import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import griddata


df = pd.read_csv('training_data.csv')

points = []
xdata = np.linspace(3.6, 58, 50)
ydata = np.linspace(1, 60, 50)
xv, yv = np.meshgrid(xdata, ydata, indexing='ij')
for i in xdata:
    for j in ydata:
        points.append((i, j))

value = griddata(df.values[:, 0:2], df.values[:, 2], points, method='linear')

fig = plt.figure()
ax = plt.axes(projection='3d')
ax.scatter3D(xv, yv, value, c=value)
ax.set_xlabel('qps')
ax.set_ylabel('quota')
ax.set_zlabel('rt')
plt.show()
