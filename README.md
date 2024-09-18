# SpaceOwl

Wifi-sensing based on the ESP32 microcontrollers. 
The project collects CSI data using ESP32 microcontrollers, data is then processed using deep learning models. This project focuses on the task of human activity recognition.

## Directory Structure
* data/: Contains CSV files of CSI data.
* esp_src/: Contains the code for ESP32 devices. It is divided into sub-projects where each of them is to be installed on a device: active_ap, active_sta. Each folder contains necessary CMake files, header, and source code.
* py_src/: Contains Python scripts used for analytics, training, inference, and utility functions.
  * train.py: Used for training deep learning models.
  * inference.py: Handles the model inference.
  * analytics.py: Provides functions to analyze the Wifi sensing data.
  * utils.py & nn_utils.py: Various utility functions used in training and inference.
* results/: Stores the generated results of the inference process, such as predictions and labels.
* timed_service/: Contains systemd service files for timed services including timed_service.py, timed_service.service, and timed_service.timer.

## Usage
1. Data Collection: ESP32 devices are configured to collect RSSI and CSI data from WIFI signals. (esp_src)
2. Training Models: The data can be processed used to train deep learning models in Python. (py_src/train.py)
3. Inference: The trained models can be used to infer human activity based on Wifi-sensing data (py_src/inference.py)
