set(IDF_TARGET esp32s3)
# Define the chip variant.

set(SDKCONFIG_DEFAULTS
    ${MICROPY_PORT_DIR}/boards/sdkconfig.base
    ${MICROPY_PORT_DIR}/boards/sdkconfig.usb
    ${MICROPY_PORT_DIR}/boards/sdkconfig.ble
    ${MICROPY_PORT_DIR}/boards/sdkconfig.spiram_sx
    ${MICROPY_PORT_DIR}/boards/ESP32_GENERIC_S3/sdkconfig.board
    # ${MICROPY_PORT_DIR}/boards/sdkconfig.240mhz
    # ${MICROPY_PORT_DIR}/boards/sdkconfig.spiram_oct
    )
    

    list(APPEND MICROPY_DEF_BOARD
        MICROPY_HW_BOARD_NAME="Generic ESP32S3 moduleM"
    )

set(USER_C_MODULES
    ${PROJECT_DIR}/cmodules/IcsParser/micropython.cmake
    ${PROJECT_DIR}/cmodules/DotMatrix/micropython.cmake
)

set(MICROPY_FROZEN_MANIFEST ${PROJECT_DIR}/manifest.py)

