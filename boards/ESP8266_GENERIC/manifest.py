# include default manifest
include("$(PORT_DIR)/boards/manifest.py")

# include our own extra...
module("datetime.py", base_path="$(BOARD_DIR)/../../modules")
module("dateHandling.py", base_path="$(BOARD_DIR)/../../modules")
module("time.py", base_path="$(BOARD_DIR)/../../modules")
module("msgpack.py", base_path="$(BOARD_DIR)/../../modules")
package("slim", base_path="$(BOARD_DIR)/../../modules/micropython-wifi-setup/lib")
# package("micro_web_srv_2", base_path="$(BOARD_DIR)/../../modules/micropython-wifi-setup/lib")
module("logging.py","$(BOARD_DIR)/../../modules/micropython-wifi-setup/lib")
module("micro_dns_srv.py","$(BOARD_DIR)/../../modules/micropython-wifi-setup/lib")
module("shim.py","$(BOARD_DIR)/../../modules/micropython-wifi-setup/lib")
module("schedule.py","$(BOARD_DIR)/../../modules/micropython-wifi-setup/lib")
module("frozen_wifi_setup.py", base_path="$(BOARD_DIR)/../../modules")
module("frozen_micro_web_srv_2.py", base_path="$(BOARD_DIR)/../../modules")
