# This file is executed on every boot (including wake-boot from deepsleep)
from wifi_manager import WifiManager
from ota_update import ota_update
import gc

gc.collect()  # Free up memory
gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
print("free mem:", gc.mem_free())

wm = WifiManager(ssid="temp-and-pressure",password="my password")
wm.connect()

ota_update()    # Check for OTA updates

gc.collect()  # Free up memory
print("free mem:", gc.mem_free())
