

import numpy as np
import torch
from torch.utils.data import DataLoader, random_split, TensorDataset

# Assuming you have a NumPy array input_data of shape (519936, 2)
input_data = np.random.rand(519936, 2)
# Assuming you have corresponding labels, replace this with your actual labels
labels = np.random.randint(0, 2, size=(519936,))

# Convert NumPy arrays to PyTorch tensors
inputs = torch.tensor(input_data, dtype=torch.float32)
labels = torch.tensor(labels, dtype=torch.long)  # Assuming labels are integers

# Combine inputs and labels into a TensorDataset
dataset = TensorDataset(inputs, labels)

# Define the sizes for train, validation, and test sets
train_size = int(0.8 * len(dataset))
val_size = int(0.1 * len(dataset))
test_size = len(dataset) - train_size - val_size

# Split the dataset into train, validation, and test sets
train_dataset, val_dataset, test_dataset = random_split(dataset, [train_size, val_size, test_size])

# Define batch sizes
batch_size = 64

# Create DataLoader instances for train, validation, and test sets
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
