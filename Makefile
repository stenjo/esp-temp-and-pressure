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
	$(MAKE) -C $(PORT_DIR) BOARD=$(BOARD) FROZEN_MANIFEST=$(FROZEN_MANIFEST) clean

# Deploy rule
deploy:
	$(MAKE) -C $(PORT_DIR) BOARD=$(BOARD) PORT=$(PORT) FROZEN_MANIFEST=$(FROZEN_MANIFEST) deploy

# Erase rule
erase:
	$(MAKE) -C $(PORT_DIR) BOARD=$(BOARD) PORT=$(PORT) FROZEN_MANIFEST=$(FROZEN_MANIFEST) erase

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
	rshell -p $(REPL) rm /pyboard/boot.py
	rshell -p $(REPL) cp -r src/main.py /pyboard
	rshell -p $(REPL) cp -r src/wifi.dat /pyboard
	rshell -p $(REPL) cp -r src/version.txt /pyboard
	rshell -p $(REPL) cp -r src/boot.py /pyboard
	sleep 2
