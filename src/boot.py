# This file is executed on every boot (including wake-boot from deepsleep)
from wifi_manager import WifiManager
import gc
import machine

gc.collect()  # Free up memory
gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
print("free mem:", gc.mem_free())

wm = WifiManager(ssid="temp-and-pressure",password="my password")
wm.connect()

gc.collect()  # Free up memory
print("free mem:", gc.mem_free())
