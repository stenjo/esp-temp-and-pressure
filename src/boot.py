# This file is executed on every boot (including wake-boot from deepsleep)
import frozen_micro_web_srv_2
# import frozen_slim
import frozen_wifi_setup
# import wifi_setup
import network
import gc

gc.collect()  # Free up memory
gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
print("free mem:", gc.mem_free())

from wifi_setup.wifi_setup import WiFiSetup

ws = WiFiSetup("temp-and-pressure")
sta = ws.connect_or_setup()
del ws

gc.collect()  # Free up memory
print("free mem:", gc.mem_free())
