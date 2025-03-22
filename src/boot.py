# This file is executed on every boot (including wake-boot from deepsleep)
from wifi_manager import WifiManager
import gc
import micropython_ota
from creds import get_creds

gc.collect()  # Free up memory
gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
print("free mem:", gc.mem_free())

wm = WifiManager(ssid="temp-and-pressure",password="my password")
wm.connect()

# host, project, filenames, use_version_prefix=True, user=None, passwd=None, hard_reset_device=True, soft_reset_device=False, timeout=5
user,passwrd = get_creds()
micropython_ota.ota_update(
    host='http://192.168.1.2:8000',
    project='esp-temp-and-pressure',
    filenames=['boot.py', 'creds.py', 'main.py'],
    user=user,
    passwd=passwrd,
    use_version_prefix=False)

gc.collect()  # Free up memory
print("free mem:", gc.mem_free())
