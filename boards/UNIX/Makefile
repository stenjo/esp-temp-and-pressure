# Makefile for custom MicroPython stm32 board.

################################################################################
# Define your settings here.

# The board name.
BOARD ?= UNIX
VARIANT ?= "coverage"

# Location of MicroPython repository.
MICROPY_TOP ?= $(abspath ../../lib/micropython)
PROJECT_TOP ?= $(abspath ../..)
USER_C_MODULES ?= $(abspath $(PROJECT_TOP)/cmodules)
# USER_C_MODULES ?= $(abspath ../../lib/micropython/examples/usercmodule)
################################################################################
# Define your targets here.

all: firmware

################################################################################
# Items below this line do not generally need to be changed.

BOARD_DIR = $(abspath .)
BUILD = $(abspath build)

include $(MICROPY_TOP)/py/mkenv.mk
include $(MICROPY_TOP)/py/mkrules.mk
include $(BOARD_DIR)/mpconfigport.mk

firmware:
	$(Q)$(MAKE) -C $(MICROPY_TOP)/ports/unix \
		PROJECT_TOP=$(abspath ../..) \
		BOARD=$(BOARD) \
		BOARD_DIR=$(BOARD_DIR) \
		BUILD=$(BUILD) \
		FROZEN_MANIFEST=$(FROZEN_MANIFEST) \
		USER_C_MODULES=$(USER_C_MODULES) \
		VARIANT=$(VARIANT)

prepare:
	$(ECHO) "Preparing submodules and frozen files"
	git submodule update --init $(MICROPY_TOP)
	git submodule update --init $(PROJECT_TOP)/modules/micropython-wifi-setup
	git submodule update --init $(PROJECT_TOP)/modules/mrequests
	make -C $(MICROPY_TOP)/mpy-cross
	$(Q)$(MAKE) -C $(MICROPY_TOP)/ports/unix submodules
	python -m freezefs $(PROJECT_TOP)/modules/micropython-wifi-setup/lib/wifi_setup $(PROJECT_TOP)/modulesfrozen_wifi_setup.py -ov always
	python -m freezefs $(PROJECT_TOP)/modules/micropython-wifi-setup/lib/micro_web_srv_2 $(PROJECT_TOP)/modulesfrozen_micro_web_srv_2.py -ov always


deploy:
	$(PYTHON) $(MICROPY_TOP)/tools/pydfu.py -u $(BUILD)/firmware.dfu

test: firmware
	MICROPYPATH=../../modules ./build/micropython ../../tests/test_ics.py

