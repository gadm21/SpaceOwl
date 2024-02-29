import torch
import torch.nn as nn
import torch.optim as optim
from utils import parse_csi, get_data_files

class CSIModel(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(CSIModel, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)
        self.sf = nn.Softmax(dim=1)

    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        output = self.fc(lstm_out[:, -1, :])
        output = self.sf(output)
        return output

import torch.nn.functional as F

class ComplexCSIModel(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size, dropout_rate=0.2):
        super(ComplexCSIModel, self).__init__()
        
        self.lstm_layers = nn.ModuleList([nn.LSTM(input_size if i == 0 else hidden_size,
                                                 hidden_size,
                                                 batch_first=True) for i in range(num_layers)])
        
        self.dropout = nn.Dropout(p=dropout_rate)
        self.fc = nn.Linear(hidden_size, output_size)
        self.sf = nn.Softmax(dim=1)

    def forward(self, x):
        batch_size, seq_len, _ = x.size()
        
        # Initialize hidden state for each layer
        h_states = [torch.zeros(1, batch_size, self.lstm_layers[i].hidden_size).to(x.device) for i in range(len(self.lstm_layers))]
        c_states = [torch.zeros(1, batch_size, self.lstm_layers[i].hidden_size).to(x.device) for i in range(len(self.lstm_layers))]
        
        # LSTM layers
        for i in range(len(self.lstm_layers)):
            x, (h_states[i], c_states[i]) = self.lstm_layers[i](x, (h_states[i], c_states[i]))
            x = F.relu(x)  # Apply ReLU activation between layers
            x = self.dropout(x)  # Apply dropout for regularization
        
        # Only take the output from the last time step
        x = x[:, -1, :]
        
        # Fully connected layer
        x = self.fc(x)
        
        # Softmax activation
        output = self.sf(x)
        
        return output


def train(model, train_loader, criterion, optimizer, num_epochs=10):
    model.train()
    
    for epoch in range(num_epochs):
        running_loss = 0.0
        for inputs, labels in train_loader:
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
        
        print(f'Epoch {epoch+1}/{num_epochs}, Loss: {running_loss/len(train_loader)}')

def evaluate(model, val_loader):
    model.eval()
    correct = 0
    total = 0
    
    tars, preds = [], []
    with torch.no_grad():
        for inputs, labels in val_loader:
            outputs = model(inputs)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            tars.extend(labels)
            preds.extend(predicted)

    tars = [t.item() for t in tars]
    preds = [p.item() for p in preds]
    # to numpy
    tars = torch.tensor(tars).numpy()
    preds = torch.tensor(preds).numpy()
    

    accuracy = correct / total
    print(f'Accuracy on validation set: {100 * accuracy:.2f}%')

    return tars, preds