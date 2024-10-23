# Makefile for custom MicroPython stm32 board.

################################################################################
# Define your settings here.

# The board name.
BOARD ?= ESP8266_GENERIC

# Location of MicroPython repository.
MICROPY_TOP ?= $(abspath ../../lib/micropython)
PROJECT_TOP?=$(abspath ../..)

################################################################################
# Define your targets here.

all: firmware

################################################################################
# Items below this line do not generally need to be changed.

BOARD_DIR = $(abspath .)
BUILD = $(abspath build)
FWBIN = $(BUILD)/firmware.bin
PORT ?= /dev/tty.usbserial-1430
BAUD ?= 115200
FLASH_MODE ?= qio
FLASH_SIZE ?= detect
# CFLAGS += -DESP8266

# USER_C_MODULES ?= $(PROJECT_TOP)/cmodules
# FROZEN_MANIFEST ?= $(BOARD_DIR)/manifest.py

include $(MICROPY_TOP)/py/mkenv.mk
include $(MICROPY_TOP)/py/mkrules.mk

firmware:
	$(Q)$(MAKE) -j -C $(MICROPY_TOP)/ports/esp8266 \
		PROJECT_TOP=$(PROJECT_TOP) \
		BOARD=$(BOARD) \
		BOARD_DIR=$(BOARD_DIR) \
		BUILD=$(BUILD) \
		CFLAGS=$(CFLAGS)
		

deploy: $(FWBIN)
	$(ECHO) "Writing $< to the board"
	$(Q)esptool.py --port $(PORT) --baud $(BAUD) write_flash --verify --flash_size=$(FLASH_SIZE) --flash_mode=$(FLASH_MODE) 0 $<

erase:
	$(ECHO) "Erase flash"
	$(Q)esptool.py --port $(PORT) --baud $(BAUD) erase_flash

reset:
	echo -e "\r\nimport machine; machine.reset()\r\n" >$(PORT)
