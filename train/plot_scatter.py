import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv('training_data.csv')

fig = plt.figure()
ax = fig.add_subplot(projection='3d')

xs = df.values[:, 0]
ys = df.values[:, 1]
zs = df.values[:, 2]
ax.scatter(xs, ys, zs)

ax.set_xlabel('qps')
ax.set_ylabel('quota')
ax.set_zlabel('rt')

plt.show()
