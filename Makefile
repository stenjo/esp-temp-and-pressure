# Makefile for custom MicroPython esp8266 board.

################################################################################
# Define your settings here.

# The board name.
BOARD ?= ESP8266_GENERIC

# USB port
# USB ?= /dev/cu.usbserial-1410
USB ?= /dev/cu.usbserial-FTB6SPL3

# Location of MicroPython repository.
MICROPY_TOP ?= $(abspath lib/micropython)
PORT_DIR ?= $(abspath $(MICROPY_TOP)/ports/esp8266) 

FROZEN_MANIFEST?=$(abspath manifest.py)

PROJECT_TOP?=$(abspath .)

################################################################################
# Define your targets here.

all: firmware

################################################################################
# Items below this line do not generally need to be changed.
BOARD_DIR = $(abspath $(MICROPY_TOP)/ports/esp8266/boards/$(BOARD))
BUILD = $(abspath build)
FWBIN = $(BUILD)/firmware.bin
PORT ?= $(USB)
BAUD ?= 115200
FLASH_MODE ?= dio
FLASH_SIZE ?= detect
PYTHON ?= python3
USER_C_MODULES ?= $(abspath cmodules/micropython.cmake)
# USER_C_MODULES ?= $(abspath lib/micropython/examples/usercmodule/cexample/micropython.cmake)

include $(MICROPY_TOP)/py/mkenv.mk
include $(MICROPY_TOP)/py/mkrules.mk

firmware:
	$(Q)$(MAKE) -j -C $(MICROPY_TOP)/ports/esp8266 \
		PROJECT_TOP=$(abspath .) \
		BOARD=$(BOARD) \
		BOARD_DIR=$(BOARD_DIR) \
		BUILD=$(BUILD) \
		USER_C_MODULES=$(USER_C_MODULES) \
		MICROPY_FROZEN_MANIFEST=$(FROZEN_MANIFEST)

deploy: $(FWBIN)
	$(ECHO) "Writing $< to the board"
	$(Q)esptool.py --port $(PORT) --baud 1000000 write_flash --flash_size=4MB -fm dio 0 $<

# $(Q)esptool.py --chip esp8266 --port $(PORT) --baud $(BAUD) write_flash --verify --flash_size=$(FLASH_SIZE) --flash_mode=$(FLASH_MODE) 0 $<
erase:
	$(ECHO) "Erase flash"
	$(Q)esptool.py --port $(PORT) --baud $(BAUD) erase_flash

reset:
	echo -e "\r\nimport machine; machine.reset()\r\n" >$(PORT)

mon:
	picocom $(USB) --b $(BAUD)

prepare:
	$(ECHO) "Preparing submodules and frozen files"
	git submodule update --init $(MICROPY_TOP)
	git submodule update --init $(PROJECT_TOP)/modules/micropython-wifi-setup
	git submodule update --init $(PROJECT_TOP)/modules/mrequests
	$(Q)$(MAKE) -C $(MICROPY_TOP)/mpy-cross
	$(Q)$(MAKE) -C $(MICROPY_TOP)/ports/unix submodules
	python3 -m freezefs $(PROJECT_TOP)/modules/micropython-wifi-setup/lib/wifi_setup $(PROJECT_TOP)/modules/frozen_wifi_setup.py -ov always
	python3 -m freezefs $(PROJECT_TOP)/modules/micropython-wifi-setup/lib/micro_web_srv_2 $(PROJECT_TOP)/modules/frozen_micro_web_srv_2.py -ov always

copy:
	rshell -p  $(PORT) rsync src /pyboard
	sleep 2

bld:
	docker run --rm -v $HOME:$HOME -u $UID -w $PWD larsks/esp-open-sdk make PYTHON=python3

