
import re
from math import sqrt, atan2
import os 
import numpy as np
from collections import defaultdict



def get_data_files(data_dir = 'data/'): 
    return [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith('.csv')]



def generate_labels(data) : 
    # data is a list of length: n_classes and each element has shape (n_s, n_t, n_f)
    n_classes = len(data)
    n_ss = [datum.shape[0] for datum in data]
    labels = [np.zeros((n_s,)) for n_s in n_ss]
    for i in range(n_classes):
        labels[i][:] = i
    return labels



def split_csi(data, interval_len = 100) : 
    # data shape is (n_t, n_f)
    num_intervals = len(data) // interval_len
    data = np.array_split(data[:num_intervals * interval_len], num_intervals)
    return np.array(data) 



def parse_csi(filename, macs = None, csi_only = False):
    print("reading file: ", filename)
    
    csis = []
    found_macs = []
    corrupt_lines = 0
    lines = 0
    with open(filename, 'r') as f:
        for j, l in enumerate(f.readlines()):
            lines += 1
            imaginary = []
            real = []
            amplitudes = []
            phases = []

            # Parse string to create integer list
            try : 
                csi_string = re.findall(r"\[(.*)\]", l)[0]
                
                mac = re.findall(r"([0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2})", l)[0]
  
                if macs is not None and mac not in macs:
                    continue
                csi_raw = [int(x) for x in csi_string.split(" ") if x != '']
                assert len(csi_raw) == 384
                found_macs.append(mac)
            except :
                corrupt_lines += 1
                continue

            # Create list of imaginary and real numbers from CSI
            for i in range(len(csi_raw)):
                if i % 2 == 0:
                    imaginary.append(csi_raw[i])
                else:
                    real.append(csi_raw[i])

            # Transform imaginary and real into amplitude and phase
            amps = np.zeros(len(imaginary))
            phases = np.zeros(len(imaginary))
            for i in range(int(len(csi_raw) //2 )):
                amp = sqrt(imaginary[i] ** 2 + real[i] ** 2)
                phase = atan2(imaginary[i], real[i])
                amps[i] = amp
                phases[i] = phase
            csi = np.concatenate([amps, phases])
            csis.append(csi)
        if corrupt_lines > 4000 : 
            raise ValueError(f"Many ({corrupt_lines}/{lines}) corrupt lines in file {filename}")
        else : 
            print(f"Found {corrupt_lines}/{lines} corrupt lines in file {filename}")
        
    csis = np.array(csis)
    found_macs = np.array(found_macs)
    if csi_only : 
        return csis
    return csis, found_macs



if __name__ == "__main__":
    data_dir = 'data/'
    files_path = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith('.csv')]
    csis = []
    macs = []
    for f in files_path:
        csi, mac_ids = parse_csi(f)
        csi = split_csi(csi, 1000)
        csis.append(csi)
        macs.append(mac_ids)
    labels = generate_labels(csis)

    for i, (csi, label) in enumerate(zip(csis, labels)):
        print(f"File {files_path[i]}")
        print(f"CSI shape: {csi.shape}")
        print(f"Labels shape: {label.shape}")
        print()
    csi = np.concatenate(csis, axis=0)
    print(csi.shape) 
    labels = np.concatenate(labels, axis=0)
    print(labels.shape)
    # for csi, label in zip(csis, labels):
    #     print(f"CSI shape: {csi.shape}")
    #     print(f"Labels shape: {label.shape}")
    #     print()