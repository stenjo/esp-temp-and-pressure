################################################################################
# Define your settings here.

# The board name.
BOARD ?= LOLIN_S2_MINI

MICROPY_TOP ?= $(abspath lib/micropython)
PORT_DIR ?= $(abspath $(MICROPY_TOP)/ports/esp32) 
FROZEN_MANIFEST ?= $(abspath manifest.py)
# FROZEN_MANIFEST = /Users/sten/git/temp-and-pressure-sensor/manifest.py

# Define variables 
PORT = /dev/tty.usbmodem01
USB ?= /dev/cu.usbmodem01
REPL ?= /dev/tty.usbmodem14201
BAUD ?= 115200

PYTHON ?= python3

# Default target
all: deploy

# Clean rule
clean:
	# rm /Users/sten/git/temp-and-pressure-sensor/lib/micropython/ports/esp32/managed_components/espressif__tinyusb/.component_hash
	$(MAKE) -C $(PORT_DIR) BOARD=$(BOARD) FROZEN_MANIFEST=$(FROZEN_MANIFEST) clean

# Deploy rule
deploy:
	$(MAKE) -C $(PORT_DIR) BOARD=$(BOARD) PORT=$(PORT) FROZEN_MANIFEST=$(FROZEN_MANIFEST) deploy

# Erase rule
erase:
	esptool.py -p $(PORT) -b 460800 --before default_reset --after no_reset --chip esp32s2 erase_flash
	sleep 2

# $(MAKE) -C $(PORT_DIR) BOARD=$(BOARD) PORT=$(PORT) FROZEN_MANIFEST=$(FROZEN_MANIFEST) erase -- --after no_reset

# Monitor rule
monitor:
	$(MAKE) -C $(PORT_DIR) BOARD=$(BOARD) PORT=$(PORT) FROZEN_MANIFEST=$(FROZEN_MANIFEST) monitor

# Size rule
size:
	$(MAKE) -C $(PORT_DIR) BOARD=$(BOARD) FROZEN_MANIFEST=$(FROZEN_MANIFEST) size

test:
	$(MAKE) -C $(PORT_DIR) BOARD=$(BOARD) test

reset:
	rshell -p $(REPL) "repl ~ import machine ~ machine.reset() ~"
	sleep 2

mon:
	picocom $(REPL) --b $(BAUD)

prepare:
	$(Q)$(MAKE) -C $(MICROPY_TOP)/mpy-cross
	$(Q)$(MAKE) -C $(MICROPY_TOP)/ports/unix submodules
	$(Q)$(MAKE) -C $(MICROPY_TOP)/ports/esp8266 submodules

update:
	git submodule update --init $(MICROPY_TOP)

copy:
	rshell -p $(REPL) rm /pyboard/boot.py
	rshell -p $(REPL) rsync src /pyboard
	rshell -p $(REPL) cp -r src/boot.py /pyboard
	sleep 2

copy_main:
	rshell -p $(REPL) rm -rf /pyboard/*
	rshell -p $(REPL) cp -r src/main.py /pyboard
	rshell -p $(REPL) cp -r src/wifi.dat /pyboard
	rshell -p $(REPL) cp -r src/update.dat /pyboard
	rshell -p $(REPL) cp -r src/version /pyboard
	rshell -p $(REPL) cp -r src/creds.py /pyboard
	rshell -p $(REPL) cp -r src/boot.py /pyboard
	sleep 2
