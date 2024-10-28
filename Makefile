# Makefile for custom MicroPython esp8266 board.

################################################################################
# Define your settings here.

# The board name.
BOARD ?= ESP8266_GENERIC

# USB port
USB ?= /dev/cu.usbserial-210
# USB ?= /dev/cu.usbserial-FTB6SPL3

# Location of MicroPython repository.
MICROPY_TOP ?= $(abspath lib/micropython)
PORT_DIR ?= $(abspath $(MICROPY_TOP)/ports/esp8266) 

# FROZEN_MANIFEST?=$(PORT_DIR)/boards/$(BOARD)/manifest_512kiB.py
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
		FROZEN_MANIFEST=$(FROZEN_MANIFEST)

deploy: $(FWBIN)
	$(ECHO) "Writing $< to the board"
	$(Q)esptool.py --port $(PORT) --baud 1000000 write_flash --flash_size=4MB -fm dio 0 $<

# $(Q)esptool.py --chip esp8266 --port $(PORT) --baud $(BAUD) write_flash --verify --flash_size=$(FLASH_SIZE) --flash_mode=$(FLASH_MODE) 0 $<
erase:
	$(ECHO) "Erase flash"
	$(Q)esptool.py --port $(PORT) --baud $(BAUD) erase_flash

reset:
	rshell -p $(PORT) "repl ~ import machine ~ machine.reset() ~"
	sleep 2

mon:
	picocom $(USB) --b $(BAUD)

prepare:
	$(ECHO) "Preparing submodules and frozen files"
	$(Q)$(MAKE) -C $(MICROPY_TOP)/mpy-cross
	$(Q)$(MAKE) -C $(MICROPY_TOP)/ports/unix submodules
	$(Q)$(MAKE) -C $(MICROPY_TOP)/ports/esp8266 submodules

update:
	git submodule update --init $(MICROPY_TOP)

copy:
	rshell -p  $(PORT) rsync src /pyboard
	sleep 2

bld:
	docker run --rm -v $HOME:$HOME -u $UID -w $PWD larsks/esp-open-sdk make PYTHON=python3

