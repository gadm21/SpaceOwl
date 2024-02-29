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
        print("received: ", l)
        if "ssid" in l.lower():
            home_ssid = l.split(":")[1]
        if "password" in l.lower():
            home_password = l.split(":")[1]
    
    ser.close()
    print("received ssid and password: ", home_ssid, home_password) 
    print("connecting to {} with password {}".format(home_ssid, home_password))
    connect_to(home_ssid, home_password)


# a function that starts a thread and listens to the serial port
def starting_threads():
    thread = threading.Thread(target=listen_to_serial, args=(get_port(), 115200))
    thread.start()
    thread.join()  # Wait for the thread to finish

def main() : 
    starting_threads()
    print("got ssid and password: ", home_ssid, " ", home_password)
    sleep(5) 
    print("disconnecting from current wifi")
    disconnect()
    sleep(5)
    print("______")
    print("ssid") 
    for i, h in enumerate(home_ssid) : 
        print(i, ":", h)
    print("______")
    print("password")
    for i, p in enumerate(home_password) : 
        print(i, ":", p)
    print("______")
    sleep(5)
    print("connecting to ", home_ssid, " with password ", home_password)
    connect_to(home_ssid, home_password)
    sleep(5)

    print("connected to ", home_ssid, " with password ", home_password)
    



if __name__ == "__main__":
    main()
