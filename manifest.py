# include default manifest
include("$(PORT_DIR)/boards/manifest.py")

# include our own extra...
# module("datetime.py", base_path="modules")
package("mrequests", base_path="modules/mrequests")
module("time.py", base_path="modules")
module("simple.py", base_path="modules/mqtt")
package("slim", base_path="modules/micropython-wifi-setup/lib")
package("micro_web_srv_2", base_path="modules/micropython-wifi-setup/lib")
# module("logging.py","modules/micropython-wifi-setup/lib")
module("micro_dns_srv.py","modules/micropython-wifi-setup/lib")
module("shim.py","modules/micropython-wifi-setup/lib")
module("schedule.py","modules/micropython-wifi-setup/lib")
module("frozen_wifi_setup.py", base_path="modules")
module("frozen_micro_web_srv_2.py", base_path="modules")
