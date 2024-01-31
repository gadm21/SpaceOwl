import numpy as np
import torch
from torch.utils.data import DataLoader, random_split, TensorDataset
import torch.nn as nn
import torch.optim as optim

from nn_utils import CSIModel, train, evaluate, ComplexCSIModel
from utils import parse_csi, get_data_files, generate_labels, split_csi

import os

def train_csi(data_dir = 'data') : 
    file_paths = get_data_files(data_dir)
    data = [split_csi(parse_csi(f, csi_only = True), 1000) for f in file_paths]
    labels = generate_labels(data)
    data = np.concatenate(data, axis=0)
    labels = np.concatenate(labels, axis=0)
    print("shape of data: ", data.shape)
    print("shape of labels: ", labels.shape)

    inputs = torch.tensor(data, dtype=torch.float32)
    labels = torch.tensor(labels, dtype=torch.long)
    dataset = TensorDataset(inputs, labels)
    train_dataset, val_dataset, test_dataset = \
        random_split(dataset, [int(0.8 * len(dataset)), int(0.1 * len(dataset)), len(dataset) - int(0.8 * len(dataset)) - int(0.1 * len(dataset))])
    train_loader, val_loader, test_loader = DataLoader(train_dataset, batch_size=640, shuffle=True), DataLoader(val_dataset, batch_size=64, shuffle=False), DataLoader(test_dataset, batch_size=64, shuffle=False)

    input_size = 3
    hidden_size = 15
    output_size = len(np.unique(labels))
    model = ComplexCSIModel(input_size, hidden_size, num_layers= 20, output_size=output_size, dropout_rate=0.2)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.008)

    # Train the model
    train(model, train_loader, criterion, optimizer, num_epochs=10)

    # Evaluate the model on the validation set
    tars, preds = evaluate(model, val_loader)

    # save targets and predictions
    results_dir = 'results'
    np.save(os.path.join(results_dir,'targets.npy'), tars)
    np.save(os.path.join(results_dir, 'predictions.npy'), preds)

if __name__ == '__main__':
    train_csi()
