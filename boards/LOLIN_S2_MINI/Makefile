# Makefile for custom MicroPython esp32 board.

MICROPY_TOP ?= $(abspath ../../lib/micropython)
MICROPY_DIRECTORY ?= $(abspath ../../lib/micropython)
BOARD = ESP32_GENERIC_S2
# lib/micropython/ports/esp32/boards/ESP32_GENERIC_S3
BOARD_VARIANT = esp32s2
PORT_DIR = $(MICROPY_TOP)/ports/esp32/
BOARD_DIR = $(PORT_DIR)/boards/$(BOARD)/
BUILD = $(abspath build)

FWBIN = $(BUILD)/firmware.bin
MPBIN = $(BUILD)/micropython.bin
FWSRC = $(BUILD)/firmware_lfs.bin
PARTBIN = $(BUILD)/partition-table.bin
LFS = $(BUILD)/littlefs.img
PORT ?= /dev/cu.usbmodem01
REPL ?= /dev/cu.usbmodem1234561
BAUD ?= 460800
FLASH_MODE ?= dio
FLASH_SIZE ?= 4MB #detect
V=1

all: firmware

# include $(MICROPY_TOP)/py/mkenv.mk
include $(MICROPY_TOP)/py/mkrules.mk

firmware:
	idf.py build 

deploy:
	$(ECHO) "Writing $< to the board"
	$(Q)esptool.py --chip esp32s2 -p $(PORT) -b $(BAUD) \
	--before no_reset \
	--after no_reset \
	write_flash \
	--flash_mode=$(FLASH_MODE) \
	--flash_size=$(FLASH_SIZE) \
	--flash_freq 80m \
	0x1000  $(BUILD)/bootloader/bootloader.bin \
	0x8000  $(BUILD)/partition_table/partition-table.bin \
	0x10000 $(MPBIN)

merge:
	$(ECHO) "Merge binary with src/ folder files"
	$(Q)vfsmerge  --port esp32-s2 --firmware $(MPBIN)
	$(Q)esptool.py --chip esp32s2 merge_bin -o $(FWSRC) \
	--flash_mode=$(FLASH_MODE) \
	--flash_size=$(FLASH_SIZE) \
	--flash_freq 80m \
	0x1000 $(BUILD)/bootloader/bootloader.bin \
	0x8000 $(BUILD)/partition_table/partition-table.bin \
	0x10000 $(MPBIN) \
	0x00200000 $(LFS)

merge-firmware:
	$(ECHO) "Merge micropython binary with bootloader and partition-table"
	$(Q)esptool.py --chip esp32s2 merge_bin -o $(FWBIN) \
	--flash_mode=keep \
	--flash_size=$(FLASH_SIZE) \
	--flash_freq keep \
	0x1000 $(BUILD)/bootloader/bootloader.bin \
	0x8000 $(BUILD)/partition_table/partition-table.bin \
	0x10000 $(MPBIN)

deploy-merged:
	$(ECHO) "Writing $< to the board"
	$(Q)esptool.py --chip esp32s2 -p $(PORT) -b $(BAUD) \
	--before default_reset \
	--after hard_reset \
	write_flash \
	--flash_mode=$(FLASH_MODE) \
	--flash_size=$(FLASH_SIZE) \
	--flash_freq 80m 0x0 \
	$(FWSRC)


	# 0x1000 $(BUILD)/bootloader/bootloader.bin \
	# 0x8000 $(BUILD)/partition_table/partition-table.bin \
	# 0x10000 $(FWBIN) \
	# 0x00200000 $(LFS) 

erase:
	$(ECHO) "Erase flash"
	$(Q)esptool.py --after no_reset --port $(PORT) --baud $(BAUD) erase_flash
	sleep 1

reset:
	echo -e "\r\nimport machine; machine.reset()\r\n" >$(REPL)

clean:
	idf.py fullclean
	rm -rf build

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
	$(Q)wget https://github.com/stenjo/dot-matrix-calendar/releases/latest/download/$(BOARD_VARIANT).zip
	unzip $(BOARD_VARIANT).zip
