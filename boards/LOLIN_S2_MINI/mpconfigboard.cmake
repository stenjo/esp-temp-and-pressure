# Define the chip variant.
set(IDF_TARGET esp32s2)

set(SDKCONFIG_DEFAULTS
    ${MICROPY_PORT_DIR}/boards/sdkconfig.base
    ${MICROPY_PORT_DIR}/boards/sdkconfig.spiram_sx
    ${MICROPY_PORT_DIR}/boards/sdkconfig.usb
)

# Set the user C modules to include in the build.
set(USER_C_MODULES
    ${PROJECT_DIR}/cmodules/IcsParser/micropython.cmake
    ${PROJECT_DIR}/cmodules/DotMatrix/micropython.cmake
)

set(MICROPY_FROZEN_MANIFEST ${PROJECT_DIR}/manifest.py)
