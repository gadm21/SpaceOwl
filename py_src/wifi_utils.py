import subprocess

def what_wifi():
    process = subprocess.run(['nmcli', '-t', '-f', 'ACTIVE,SSID', 'dev', 'wifi'], stdout=subprocess.PIPE)
    ssid = '' 
    for line in process.stdout.decode('utf-8').strip().split('\n'):
        if 'yes' in line.lower().split(':')[0]:
            ssid = line.split(':')[1]
    return ssid
    # if process.returncode == 0:
    #     return process.stdout.decode('utf-8').strip().split(':')[1]
    # else:
    #     return ''

def is_connected_to(ssid: str):
    return what_wifi() == ssid

def scan_wifi():
    process = subprocess.run(['sudo', 'nmcli', '-t', '-f', 'SSID,SECURITY,SIGNAL', 'dev', 'wifi'], stdout=subprocess.PIPE)
    if process.returncode == 0:
        return process.stdout.decode('utf-8').strip().split('\n')
    else:
        return []
        
def is_wifi_available(ssid: str):
    return ssid in [x.split(':')[0] for x in scan_wifi()]

def connect_to(ssid: str, password: str):
    if not is_wifi_available(ssid):
        return False
    subprocess.call(['nmcli', 'd', 'wifi', 'connect', ssid, 'password', password])
    return is_connected_to(ssid)

def connect_to_saved(ssid: str):
    if not is_wifi_available(ssid):
        return False
    subprocess.call(['nmcli', 'c', 'up', ssid])
    return is_connected_to(ssid)

def disconnect(ssid: str = None):
    if ssid is None : 
        ssid = what_wifi()
        if ssid == '' : 
            return False 
    
    subprocess.call(['sudo', 'nmcli', 'con', 'down', ssid])
    return not is_connected_to(ssid)

if __name__ == "__main__":
    
    disconnect()
    connect_to('43 Hillsmount', 'Sandy@2023')