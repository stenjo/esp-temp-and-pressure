# This file is executed on every boot (including wake-boot from deepsleep)
# import frozen_wifi_setup
# import frozen_setup
# import frozen_micro_web_srv_2
import os, machine
import gc
gc.collect()

import network
import ntptime
import time

# from wifi_setup.wifi_setup import WiFiSetup

# ws = WiFiSetup("dot-matrix-calendar")
# sta = ws.connect_or_setup()
# del ws

sta_if = network.WLAN(network.STA_IF); sta_if.active(True)
sta_if.scan()                             # Scan for available access points
sta_if.isconnected()                      # Check for successful connection

# done = False
# #if needed, overwrite default time server
# ntptime.host = "1.europe.pool.ntp.org"
# print("Local time before synchronization: %s" %str(time.localtime()))
# while done == False:
    
#     try:
#         done = True
#         #make sure to have internet connection
#         ntptime.settime()
        
#     except:
#         done = False        
#         print("Error syncing time. Trying again ...")
#         sta_if.scan()                             # Scan for available access points
#         sta_if.connect("IoT Dingser", "M5o8t33Vunbw") # Connect to an AP
#         sta_if.isconnected()                      # Check for successful connection

#         time.sleep(5)

#     finally:
#         print("Local time after synchronization: %s" %str(time.localtime()))

print(gc.mem_free())