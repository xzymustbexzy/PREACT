import time

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
from torch.utils.data import DataLoader


class RTModel(nn.Module):

    def __init__(self, hidden_size=8):
        super().__init__()
        self.hidden_size = hidden_size
        self.fc1 = nn.Linear(2, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(self.hidden_size, 2)
        self.sigmoid = nn.Sigmoid()
        self.omega = torch.nn.Parameter(torch.Tensor([1]))
        self.bias = torch.nn.Parameter(torch.Tensor([0]))


    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        x = self.sigmoid(x)
        y = self.omega / (1 - x[:, 0]) * x[:, 1] + self.bias
        return y


df = pd.read_csv('training_data.csv')
dataset = torch.from_numpy(df.values).float()
dataset[:, 0] = dataset[:, 0] / 60
dataset[:, 1] = dataset[:, 1] / 80

data_loader = DataLoader(dataset, batch_size=32, shuffle=True)

model = RTModel()
criterion = nn.MSELoss()
optimizer = torch.optim.SGD(model.parameters(), lr=1e-5, momentum=0.9)
total_epoch = 100

begin_time = time.time()

for epoch in range(total_epoch):
    total_losses = []
    for data in data_loader:
        optimizer.zero_grad()
        x = data[:, :2]
        y = data[:, 2]
        y_pred = model(x)
        loss = criterion(y_pred, y)
        loss.backward()
        optimizer.step()
        # print(y)
        # print(y_pred)
        # print(loss)
        # raise NotImplementedError
        total_losses.append(float(loss.item()))
    # raise NotImplementedError
    print(f'Epoch: {epoch}, loss: {sum(total_losses) / len(total_losses)}')

end_time = time.time()
print(f'Time usage: {end_time - begin_time} s')

points = []
xdata = np.linspace(3.6, 58, 50)
ydata = np.linspace(1, 60, 50)
for i in xdata:
    for j in ydata:
        points.append((i, j))
points = torch.tensor(points).float()
points[:, 0] = points[:, 0] / 60
points[:, 1] = points[:, 1] / 80

begin_time = time.time()

with torch.no_grad():
    value = model(points)

end_time = time.time()
print(f'Inference time: {end_time - begin_time} s')


xv, yv = np.meshgrid(xdata, ydata, indexing='ij')
fig = plt.figure()
ax = plt.axes(projection='3d')
ax.scatter3D(xv, yv, value, c=value)
ax.set_xlabel('qps')
ax.set_ylabel('quota')
ax.set_zlabel('rt')
plt.show()
