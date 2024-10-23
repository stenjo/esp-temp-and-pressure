# Makefile for custom MicroPython esp32 board.

MICROPY_TOP ?= $(abspath ../../lib/micropython)
MICROPY_DIRECTORY ?= $(abspath ../../lib/micropython)
BOARD = ESP32_GENERIC_S3
# lib/micropython/ports/esp32/boards/ESP32_GENERIC_S3
BOARD_VARIANT = esp32s3
PORT_DIR = $(MICROPY_TOP)/ports/esp32/
BOARD_DIR = $(PORT_DIR)/boards/$(BOARD)/
BUILD = $(abspath build)

FWBIN = $(BUILD)/firmware.bin
MPBIN = $(BUILD)/micropython.bin
FWSRC = $(BUILD)/firmware_lfs.bin
PARTBIN = $(BUILD)/partition-table.bin
LFS = $(BUILD)/littlefs.img
PORT ?= /dev/cu.usbmodem101
REPL ?= /dev/cu.usbmodem1234561
BAUD ?= 460800
PYTHON ?= python3
FLASH_MODE ?= dio
FLASH_SIZE ?= keep #4MB #detect
V=1
MICROPY_BOARD_VARIANT ?= SPIRAM_OCT

all: firmware

include $(MICROPY_TOP)/py/mkenv.mk
include $(MICROPY_TOP)/py/mkrules.mk

firmware:
	idf.py build

deploy:
	$(ECHO) "Writing $< to the board"
	$(Q)esptool.py --chip $(BOARD_VARIANT) -p $(PORT) -b $(BAUD) \
	--before default_reset \
	--after no_reset \
	write_flash \
	--flash_mode $(FLASH_MODE) \
	--flash_size $(FLASH_SIZE) \
	--flash_freq 80m \
	0x0 $(BUILD)/bootloader/bootloader.bin \
	0x8000 $(BUILD)/partition_table/partition-table.bin \
	0x10000 $(MPBIN)


erase:
	$(Q)esptool.py --after no_reset --port $(PORT) --baud $(BAUD) erase_flash
	sleep 1

reset:
	echo -e "\r\nimport machine; machine.reset()\r\n" >$(REPL)
	sleep 1

clean:
	rm -rf build
	idf.py fullclean

copy:
	rshell rsync ../../src /pyboard
	rshell "repl ~ import machine ~ machine.reset() ~"
	sleep 1

mon:
	picocom $(REPL) --b 115200

latest:
	rm -rf build
	rm -rf *.zip
	$(Q)wget https://github.com/stenjo/dot-matrix-calendar/releases/latest/download/$(BOARD_VARIANT).zip
	unzip $(BOARD_VARIANT).zip

latest-src:
	rm -rf build
	rm -rf *.zip
    wget https://github.com/stenjo/dot-matrix-calendar/releases/latest/download/$(BOARD_VARIANT).zip
	unzip $(BOARD_VARIANT).zip
