# include default manifest
# include("$(PORT_DIR)/boards/manifest.py")
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
# require("ssd1306")

# micropython-lib: file utilities
require("upysh")

# micropython-lib: umqtt
require("umqtt.simple")
# require("umqtt.robust")

# require("urequests")

package("mrequests", base_path="modules/mrequests")
module("ads1x15.py",base_path="modules")
package("slim", base_path="modules/micropython-wifi-setup/lib")
# package("micro_web_srv_2", base_path="modules/micropython-wifi-setup/lib")
module("logging.py","modules/micropython-wifi-setup/lib")
module("micro_dns_srv.py","modules/micropython-wifi-setup/lib")
module("shim.py","modules/micropython-wifi-setup/lib")
module("schedule.py","modules/micropython-wifi-setup/lib")
module("frozen_wifi_setup.py", base_path="modules")
# module("frozen_slim.py", base_path="modules")
module("frozen_micro_web_srv_2.py", base_path="modules")
# package("wifi_setup", base_path="modules/micropython-wifi-setup/lib")