LD_FILES = $(BOARD_DIR)/esp8266_2MiB.ld

MICROPY_PY_ESPNOW ?= 1
MICROPY_PY_BTREE ?= 1
MICROPY_VFS_FAT ?= 1
MICROPY_VFS_LFS2 ?= 1

# Add asyncio and extra micropython-lib packages (in addition to the port manifest).
FROZEN_MANIFEST ?= $(BOARD_DIR)/manifest.py

# Custom C modules
# USER_C_MODULES = $(PROJECT_TOP)/cmodules

# Configure mpconfigboard.h.
CFLAGS += -DMICROPY_ESP8266_2M
