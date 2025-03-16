# include default manifest
# include("$(PORT_DIR)/manifest.py")
freeze("$(PORT_DIR)/modules")
require("bundle-networking")
# require("dht")
require("ds18x20")
# require("neopixel")
require("onewire")
# base modules
# include("$(PORT_DIR)/boards/manifest.py")

# asyncio
include("$(MPY_DIR)/extmod/asyncio")

# drivers
require("ssd1306")

# micropython-lib: file utilities
require("upysh")

# micropython-lib: umqtt
require("umqtt.simple")
require("umqtt.robust")

# require("urequests")

module("ads1x15.py",base_path="modules")
module("ads1118.py",base_path="modules")
module("wifi_manager.py", base_path="modules")
module("captive.py", base_path="modules")
module("lcd_i2c.py", base_path="modules/lcd_i2c")
module("const.py", base_path="modules/lcd_i2c")
module("typing.py", base_path="modules/lcd_i2c")