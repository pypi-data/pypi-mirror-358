from typing import Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim


class PimaClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.hidden1 = nn.Linear(8, 12)
        self.act1 = nn.ReLU()
        self.hidden2 = nn.Linear(12, 8)
        self.act2 = nn.ReLU()
        self.output = nn.Linear(8, 1)
        self.act_output = nn.Sigmoid()

    def forward(self, x):
        x = self.act1(self.hidden1(x))
        x = self.act2(self.hidden2(x))
        x = self.act_output(self.output(x))
        return x


def get_train_data(data_path: str) -> Tuple[torch.Tensor, torch.Tensor]:
    dataset = np.loadtxt(data_path, delimiter=",")
    train_data_input = torch.tensor(dataset[:, 0:8], dtype=torch.float32)
    train_data_output = torch.tensor(dataset[:, 8], dtype=torch.float32).reshape(-1, 1)

    return train_data_input, train_data_output


def get_trained_model(train_data_input, train_data_output):
    model = PimaClassifier()

    # preparation for training
    loss_fn = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # training
    n_epochs = 100
    batch_size = 10

    for epoch in range(n_epochs):
        for i in range(0, len(train_data_input), batch_size):
            x_batch = train_data_input[i : i + batch_size]
            y_pred = model(x_batch)
            y_batch = train_data_output[i : i + batch_size]
            loss = loss_fn(y_pred, y_batch)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

    return model
