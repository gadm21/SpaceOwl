import serial
import threading

# a function that takes ssid and password, imports wifi library and connects to the wifi
def connect_to_wifi(ssid, password):
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(ssid, password)
        while not sta_if.isconnected():
            print('connecting to network...')
    print('network config:', sta_if.ifconfig())
    return sta_if.ifconfig()


# a function that gets list of ports and returns the port that the microcontroller is connected to
def get_port():
    import serial.tools.list_ports
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if "usb" in p.device.lower():
            return p[0]

# a function that takes a port and baudrate, imports serial library and listens to the serial port
def listen_to_serial(port, baudrate):
    ser = serial.Serial()
    ser.baudrate = baudrate
    ser.port = port
    ser.open()

    ssid, password = None, None 

    while ssid is None and password is None:
        l = ser.readline().decode('utf-8')
        print("received: ", l)
        if "ssid" in l.lower():
            ssid = l.split(":")[1]
        if "password" in l.lower():
            password = l.split(":")[1]
    
    ser.close()
    print("received ssid and password: ", ssid, password)
    # connect_to_wifi(ssid, password)


# a function that starts a thread and listens to the serial port
def starting_threads():
    thread = threading.Thread(target=listen_to_serial, args=(get_port(), 115200))
    thread.start()
    thread.join()  # Wait for the thread to finish

def main() : 
    starting_threads()
    



if __name__ == "__main__":
    main()
