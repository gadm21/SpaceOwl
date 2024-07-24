import sys
import matplotlib.pyplot as plt
import math
import numpy as np
import collections
from wait_timer import WaitTimer
from read_stdin import readline, print_until_first_csi_line
import regex as re

# Set subcarrier to plot
subcarrier = 44
CSI_LEN = 57 * 2

# Wait Timers. Change these values to increase or decrease the rate of `print_stats` and `render_plot`.
print_stats_wait_timer = WaitTimer(1.0)
render_plot_wait_timer = WaitTimer(0.1)

# Deque definition
perm_amp = collections.deque(maxlen=100)
perm_phase = collections.deque(maxlen=100)
snrs = collections.deque(maxlen=100)

# Variables to store CSI statistics
packet_count = 0
total_packet_counts = 0

# Create figure for plotting
plt.ion()
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
fig.canvas.draw()
plt.show(block=False)

mac_list = [
    'A0:A3:B3:AA:76:38',
    'A0:A3:B3:80:1D:8C'
]

def cook_csi_data (rx_ctrl_info, raw_csi_data) :
    rssi = rx_ctrl_info[0]  # dbm
    noise_floor = rx_ctrl_info[11] # dbm. The document says unit is 0.25 dbm but it does not make sense.
    # do not know AGC

    # Each channel frequency response of sub-carrier is recorded by two bytes of signed characters. 
    # The first one is imaginary part and the second one is real part.
    raw_csi_data = [ (raw_csi_data[2*i] * 1j + raw_csi_data[2*i + 1]) for i in range(int(len(raw_csi_data) / 2)) ]
    raw_csi_array = np.array(raw_csi_data)    

    ## Note:this part of SNR computation may not be accurate.
    #       The reason is that ESP32 may not provide a accurate noise floor value.
    #       The underlying reason could tha AGC is not calculated explicitly 
    #       so ESP32 doc just consider noise * 0.25 dbm as a estimated value. (described in the official doc)
    #       But here I will jut use the noise value in rx_ctrl info times 1 dbm as the noise floor.
    # scale csi
    snr_db = rssi - noise_floor # dB
    snr_abs = 10**(snr_db / 10.0) # from db back to normal
    csi_sum = np.sum(np.abs(raw_csi_array)**2)
    num_subcarrier = len(raw_csi_array)
    scale = np.sqrt((snr_abs / csi_sum) * num_subcarrier)
    raw_csi_array = raw_csi_array * scale
    # print("SNR = {} dB".format(snr_db))
    #

    # Note:
    #   check https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-guides/wifi.html
    #   section 'Wi-Fi Channel State Information' 
    #   sub-carrier index : LLTF (-64~-1) + HT-LTF (0~63,-64~-1)
    # In the 40MHz HT transmission, two adjacent 20MHz channels are used. 
    # The channel is divided into 128 sub-carriers. 6 pilot signals are inserted in sub-carriers -53, -25, -11, 11, 25, 53. 
    # Signal is transmitted on sub-carriers -58 to -2 and 2 to 58.
    # assert(len(raw_csi_array) == 64 * 3), "CSI data length is not 64*3 instead it is {}.".format(len(raw_csi_array))
    # cooked_csi_array = raw_csi_array[64:]
    # rearrange to -58 ~ -2 and 2 ~ 58.
    # cooked_csi_array = np.concatenate((cooked_csi_array[-58:-1], cooked_csi_array[2:59]))
    # assert(len(cooked_csi_array) == CSI_LEN), "CSI data length is not 114"
    
    # print("RSSI = {} dBm\n".format(rssi))
    return (snr_db, raw_csi_array)


def carrier_plot(csi_data, snr):
    snrs.append(snr)
    # if snrs length is greater than csi_data length, remove the first element
    if len(snrs) > len(csi_data):
        snrs.popleft()

    ax1.cla()
    ax2.cla()
    
    # Plot CSI data
    ax1.plot(range(len(csi_data)), csi_data, color='r')
    ax1.set_xlabel("Time")
    ax1.set_ylabel("Amplitude")
    ax1.set_title("Amplitude plot of Subcarrier")
    
    # Plot SNR values
    ax2.plot(range(len(snrs)), list(snrs), color='b')
    ax2.set_xlabel("Time")
    ax2.set_ylabel("SNR")
    ax2.set_title("SNR plot")
    
    fig.canvas.flush_events()
    plt.show()


def process(res):
    
    try : 
        all_data = res.split(',')
        mac = re.findall(r"([0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2})", all_data[2])[0]
        if not mac.upper() in mac_list : 
            print(mac.upper() + " not in mac list: ", mac_list)
            return None, None 

        other_data = np.array(all_data[3: -1], dtype = np.float32)
        
        csi_data = np.array(all_data[-1].split(" ")[1: -1], dtype=np.int32)

        snr_db, cooked_csi_array = cook_csi_data(other_data, csi_data)
        csi_data = 10 * np.log10(np.abs(cooked_csi_array)**2 + 0.1)

        return snr_db, csi_data
        # print("csi shape = ", csi_data.shape)
        # print("snr shape = ", type(snr_db))
        # # csi_data = [int(c) for c in csi_data if c]
        # real = csi_data[::2]
        # imaginary = csi_data[1::2]

        # common_len = min(len(real), len(imaginary))
        # real = real[:common_len]
        # imaginary = imaginary[:common_len]

        # # Calculate amplitude and phase
        # amps = np.sqrt(np.square(real) + np.square(imaginary)) 
        # phases = np.arctan2(imaginary, real)
        
    except Exception as e : 
        print(e)
        return None, None 



def main() : 
    print_until_first_csi_line()

    while True:
        line = readline()
        if "CSI_DATA" in line:
            snr, csi_data = process(line)
            # packet_count += 1
            # total_packet_counts += 1

            # if print_stats_wait_timer.check():
            #     print_stats_wait_timer.update()
            #     print("Packet Count:", packet_count, "per second.", "Total Count:", total_packet_counts)
            #     packet_count = 0

            if render_plot_wait_timer.check() and not snr is None:
                render_plot_wait_timer.update()
                carrier_plot(csi_data, snr) 


# function to read csv file and return a list of lines 
def read_csv(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return lines

if __name__ == "__main__":
    # data_file = '../data/room_doorclosed2.csv' 
    # data = read_csv(data_file)
    # for idx in range(1, len(data)) : 
    #     line = data[idx]
    #     assert("CSI_DATA" in line), "CSI_DATA not found in line"
    #     snr, csi_data = process(line)
        
    #     if render_plot_wait_timer.check() and not snr is None: 
    #         render_plot_wait_timer.update()
    #         carrier_plot(csi_data, snr)

    main() 

