# Makefile for custom MicroPython esp32 board.

MICROPY_TOP ?= $(abspath ../../lib/micropython)
MICROPY_DIRECTORY ?= $(abspath ../../lib/micropython)
BOARD = ESP32_GENERIC
# lib/micropython/ports/esp32/boards/ESP32_GENERIC_S3
BOARD_VARIANT = esp32
PORT_DIR = $(MICROPY_TOP)/ports/esp32/
BOARD_DIR = $(PORT_DIR)/boards/$(BOARD)/
BUILD = $(abspath build)

FWBIN = $(BUILD)/firmware.bin
MPBIN = $(BUILD)/micropython.bin
FWSRC = $(BUILD)/firmware_lfs.bin
PARTBIN = $(BUILD)/partition-table.bin
LFS = $(BUILD)/littlefs.img
PORT ?= /dev/tty.usbserial-0001
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
	$(Q)esptool.py --chip esp32 -p $(PORT) -b $(BAUD) \
	--before default_reset \
	--after hard_reset \
	write_flash \
	--flash_mode=$(FLASH_MODE) \
	--flash_size=$(FLASH_SIZE) \
	--flash_freq 40m \
	0x1000  $(BUILD)/bootloader/bootloader.bin \
	0x8000  $(BUILD)/partition_table/partition-table.bin \
	0x10000 $(MPBIN)
	sleep 2

merge:
	$(ECHO) "Merge binary with src/ folder files"
	$(Q)vfsmerge  --port esp32 --firmware $(FWBIN)
	$(Q)esptool.py --chip esp32 merge_bin -o $(FWSRC) \
	--flash_mode=$(FLASH_MODE) \
	--flash_size=$(FLASH_SIZE) \
	--flash_freq 40m \
	0x1000 $(BUILD)/bootloader/bootloader.bin \
	0x8000 $(BUILD)/partition_table/partition-table.bin \
	0x10000 $(MPBIN) \
	0x00200000 $(LFS)

deploy-merged:
	$(ECHO) "Writing $< to the board"
	$(Q)esptool.py --chip esp32 -p $(PORT) -b $(BAUD) \
	--before default_reset \
	--after hard_reset \
	write_flash \
	--flash_mode=$(FLASH_MODE) \
	--flash_size=$(FLASH_SIZE) \
	--flash_freq 40m 0x0 \
	$(FWSRC)


	# 0x1000 $(BUILD)/bootloader/bootloader.bin \
	# 0x8000 $(BUILD)/partition_table/partition-table.bin \
	# 0x10000 $(FWBIN) \
	# 0x00200000 $(LFS) 

erase:
	$(ECHO) "Erase flash"
	$(Q)esptool.py --port $(PORT) --baud $(BAUD) erase_flash

reset:
	echo -e "\r\nimport machine; machine.reset()\r\n" >$(PORT)

removepy:
	echo -e "\r\nos.remove('main.py');os.remove('boot.py')\r\n" >$(PORT)

copy:
	rshell -p /dev/cu.usbserial-0001 rsync ../../src /pyboard
	sleep 2

mon:
	picocom /dev/tty.usbserial-0001 --b 115200

latest:
	rm -rf *.zip
	$(Q)wget https://github.com/stenjo/dot-matrix-calendar/releases/latest/download/$(BOARD_VARIANT).zip
	unzip $(BOARD_VARIANT).zip

latest-src:
	rm -rf build
	rm -rf *.zip
    wget https://github.com/stenjo/dot-matrix-calendar/releases/latest/download/$(BOARD_VARIANT)src.zip
	unzip $(BOARD_VARIANT)src.zip
