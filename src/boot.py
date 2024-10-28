# This file is executed on every boot (including wake-boot from deepsleep)
from wifi_manager import WifiManager
import gc

gc.collect()  # Free up memory
gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
print("free mem:", gc.mem_free())

wm = WifiManager()

# By default the SSID is WiFiManager and the password is wifimanager.
# You can customize the SSID and password of the AP for your needs:
wm = WifiManager(ssid="temp-and-pressure",password="my password")

# Start the connection:
wm.connect()

gc.collect()  # Free up memory
print("free mem:", gc.mem_free())
