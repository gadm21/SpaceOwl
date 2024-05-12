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

# Wait Timers. Change these values to increase or decrease the rate of `print_stats` and `render_plot`.
print_stats_wait_timer = WaitTimer(1.0)
render_plot_wait_timer = WaitTimer(0.2)

# Deque definition
perm_amp = collections.deque(maxlen=100)
perm_phase = collections.deque(maxlen=100)

# Variables to store CSI statistics
packet_count = 0
total_packet_counts = 0

# Create figure for plotting
plt.ion()
fig = plt.figure()
ax = fig.add_subplot(111)
fig.canvas.draw()
plt.show(block=False)


def carrier_plot(amp):
    plt.clf()
    df = np.asarray(amp, dtype=np.int32)
    # Can be changed to df[x] to plot sub-carrier x only (set color='r' also)
    plt.plot(range(100 - len(amp), 100), df[:, subcarrier], color='r')
    plt.xlabel("Time")
    plt.ylabel("Amplitude")
    plt.xlim(0, 100)
    plt.title(f"Amplitude plot of Subcarrier {subcarrier}")
    # TODO use blit instead of flush_events for more fastness
    # to flush the GUI events
    fig.canvas.flush_events()
    plt.show()


def process(res):
    

    try : 

        all_data = res.split(',')
        mac = re.findall(r"([0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2})", all_data[2])[0]
        if mac != 'A0:A3:B3:AA:76:38' : 
            return 

        other_data = np.array(all_data[3: -1], dtype = np.float32)
        
        csi_data = np.array(all_data[-1].split(" ")[1: -1], dtype=np.int32)
        # csi_data = [int(c) for c in csi_data if c]
        real = csi_data[::2]
        imaginary = csi_data[1::2]

        common_len = min(len(real), len(imaginary))
        real = real[:common_len]
        imaginary = imaginary[:common_len]

        # Calculate amplitude and phase
        amps = np.sqrt(np.square(real) + np.square(imaginary)) 
        phases = np.arctan2(imaginary, real)
        
    except Exception as e : 
        print(e)
        return

    perm_phase.append(phases)
    perm_amp.append(amps)




print_until_first_csi_line()

while True:
    line = readline()
    if "CSI_DATA" in line:
        process(line)
        packet_count += 1
        total_packet_counts += 1

        if print_stats_wait_timer.check():
            print_stats_wait_timer.update()
            print("Packet Count:", packet_count, "per second.", "Total Count:", total_packet_counts)
            packet_count = 0

        if render_plot_wait_timer.check() and len(perm_amp) > 2:
            render_plot_wait_timer.update()
            carrier_plot(perm_amp)



