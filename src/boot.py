# This file is executed on every boot (including wake-boot from deepsleep)
from wifi_manager import WifiManager
import gc
import micropython_ota
import machine

gc.collect()  # Free up memory
gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
print("free mem:", gc.mem_free())

wm = WifiManager(ssid="temp-and-pressure",password="my password")
wm.connect()


def get_passwrd():
    lines = []
    try:
        with open("update.dat") as file:
            lines = file.readlines()
    except Exception as error:
        print(error)
        pass

    return lines[0].strip()



ota_host = 'http://192.168.1.2:8000'
project_name = 'esp-temp-and-pressure'
filenames = ['boot.py', 'main.py']
user='admin',
passwd=get_passwrd()

micropython_ota.ota_update(ota_host, project_name, filenames, user=user, passwd=passwd, use_version_prefix=True, hard_reset_device=True, soft_reset_device=False, timeout=5)

gc.collect()  # Free up memory
print("free mem:", gc.mem_free())
