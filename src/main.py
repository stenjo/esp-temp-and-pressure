import gc

gc.collect()
print("Free mem: ",gc.mem_free())

# Get version

print("Free mem: ",gc.mem_free())

try:
    while True:
        print("Free mem: ",gc.mem_free())

        # if hasattr(esp32, 'raw_temperature'):
        #     tf = esp32.raw_temperature()
        #     tc = (tf-32.0)/1.8
        #     print("T = {0:4d} deg F or {1:5.1f}  deg C".format(tf,tc))
        # else:
        #     print("T = {0:4d} deg C".format(esp32.mcu_temperature()))
                    
except KeyboardInterrupt:
    print("\nControl-C pressed. Cleaning up and exiting.")
