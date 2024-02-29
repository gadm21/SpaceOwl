import serial
import threading
from wifi_utils import * 
from time import sleep
home_ssid, home_password = None, None

# a function that gets list of ports and returns the port that the microcontroller is connected to
def get_port():
    import serial.tools.list_ports
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if "usb" in p.device.lower():
            return p[0]

# a function that takes a port and baudrate, imports serial library and listens to the serial port
def listen_to_serial(port, baudrate):
    global home_ssid, home_password
    ser = serial.Serial()
    ser.baudrate = baudrate
    ser.port = port
    ser.open()

    while home_ssid is None or home_password is None:
        l = ser.readline().decode('utf-8')
        
        if "ssid" in l.lower():
            home_ssid = l.split(":")[1].strip()
        if "password" in l.lower():
            home_password = l.split(":")[1].strip()
    
    ser.close()
    
    # print("connecting to {} with password {}".format(home_ssid, home_password), end=" ... ")
    # connect_to(home_ssid, home_password)


def wifi_hacker():
    global home_ssid, home_password
    while home_ssid is None or home_password is None:
        sleep(2)
    connect_to(home_ssid, home_password)
    print("connected to ", home_ssid, " with password ", home_password)

# a function that starts a thread and listens to the serial port
def starting_threads():
    serial_listener = threading.Thread(target=listen_to_serial, args=(get_port(), 115200))
    wifi_hacker = threading.Thread(target=wifi_hacker) 
    serial_listener.start()
    wifi_hacker.start()

    return [serial_listener, wifi_hacker]
    

def main() : 
    threads = starting_threads()

    for th in threads : 
        th.join()

    print("Griot is done!")
    



if __name__ == "__main__":
    main()
