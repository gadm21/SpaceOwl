
import datetime
import os
from functools import reduce
from utils import * 

def get_time() :
    datetime_components = ['month', 'day', 'hour', 'minute', 'ampm', 'year']
        
    return {
        name : value for (name, value) in zip( datetime_components,
        datetime.datetime.now().strftime('%b-%d-%I-%M-%p-%G').split('-'))
        }

def append_to_file(filepath, line):
    with open(filepath, 'a') as f :
        f.write(line)
        f.write('\n')

timer_resolution = 1/ 5 # a trigger per second
minute = get_time()['minute']
slot = minute * timer_resolution

if slot % 2 : # LoRa. Wait for drone connection.
    wait_for_drone()
    enable_bluetooth()
else # BLE. collect data from fit band. Disable bluetooth to prepare for the LoRa communication cycle (since a reboot is required after disabling bluetooth).
    connect_collect_classify() 
    disable_bluetooth() 
    reboot()

str_line = ' '.join([ key + ':' + value for (key, value) in dict_line.items()]) 
append_to_file(filepath, str_line)
