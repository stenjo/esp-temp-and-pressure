
# MICROPY_PY_ESPNOW ?= 1
# MICROPY_PY_BTREE ?= 1
# MICROPY_VFS_FAT ?= 1
# MICROPY_VFS_LFS2 ?= 1

FROZEN_MANIFEST ?= $(BOARD_DIR)/manifest.py

# Custom C modules
SRC_USERMOD_C += $(wildcard $(PROJECT_TOP)/cmodules/IcsParser/{.|src}/*.c)
# $(PROJECT_TOP)/cmodules/IcsParser/src/*.c 
# USER_C_MODULES += $(PROJECT_TOP)/cmodules/IcsParser/src/ics_parser.c
# USER_C_MODULES += $(PROJECT_TOP)/cmodules/IcsParser/src/ics_utils.c

# Configure mpconfigboard.h.
CFLAGS_USERMOD += -I$(PROJECT_TOP)/cmodules/IcsParser
