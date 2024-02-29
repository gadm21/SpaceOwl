
# import libraries
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split, TensorDataset
import matplotlib.pyplot as plt

from utils import parse_csi, get_data_files, generate_labels, split_csi

# a function compuates the confusion matrix of a multi-class classification problem
def confusion_matrix(y_true, y_pred):
    # number of classes
    n = len(set(y_true))
    # initialize the confusion matrix
    cm = [[0] * n for i in range(n)]
    # fill in the confusion matrix
    for i in range(len(y_true)):
        cm[y_true[i]][y_pred[i]] += 1
    return cm

# a function that plots the confusion matrix
def plot_confusion_matrix(cm, classes, title='Confusion matrix', cmap=plt.cm.Blues):
    # create a figure and an axis
    fig, ax = plt.subplots()
    # plot the confusion matrix
    im = ax.imshow(cm, interpolation='nearest', cmap=cmap)
    # set the title
    ax.set_title(title)
    # create a color bar
    cbar = ax.figure.colorbar(im, ax=ax)
    # set the color bar label
    cbar.ax.set_ylabel('Number of samples', rotation=-90, va="bottom")
    # create class labels
    ax.set_xticks(np.arange(len(classes)))
    ax.set_yticks(np.arange(len(classes)))
    ax.set_xticklabels(classes)
    ax.set_yticklabels(classes)
    # rotate the x-axis labels
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    # loop over data dimensions and create text annotations
    for i in range(len(classes)):
        for j in range(len(classes)):
            text = ax.text(j, i, cm[i][j], ha="center", va="center", color="white" if cm[i][j] > np.max(cm) / 2.0 else "black")
    # set the axis labels
    ax.set_xlabel('Predicted label')
    ax.set_ylabel('True label')
    # set the aspect of the plot to equal
    ax.set_aspect('equal', adjustable='box')
    # set the title
    fig.tight_layout()
    plt.show()

# read the targets and predictions from a .npy file
def read_results(file_path):
    # read the targets and predictions
    tars = np.load(file_path + '/targets.npy')
    preds = np.load(file_path + '/predictions.npy')
    return tars, preds

if __name__ == "__main__":
    # read the targets and predictions
    tars, preds = read_results('results')
    # compute the confusion matrix
    cm = confusion_matrix(tars, preds)

    filenames = get_data_files('data')
    filenames = [f.split('/')[-1] for f in filenames]

    # plot the confusion matrix
    plot_confusion_matrix(cm, classes= filenames, title='Confusion matrix')
    # print the confusion matrix
    print(cm)
    # compute the accuracy
    accuracy = np.trace(cm) / np.sum(cm)
    print(f'Accuracy: {accuracy}')