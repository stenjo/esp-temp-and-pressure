MAKEOPTS="-j$(sysctl -n hw.ncpu)"

########################################################################################
# ports/esp32

function ci_esp32_idf50_setup {
    pip3 install pyelftools
    git clone https://github.com/espressif/esp-idf.git
    git -C esp-idf checkout v5.0.2
    ./esp-idf/install.sh
}

function ci_esp32_build {
    source ~/esp/esp-idf/export.sh
    make ${MAKEOPTS} -C ../../lib/micropython/mpy-cross
    make ${MAKEOPTS} -C ../../lib/micropython/ports/esp32 submodules
    make ${MAKEOPTS} -C ../../lib/micropython/ports/esp32 \
        BOARD=ESP32_GENERIC_S2 \
        USER_C_MODULES=$(pwd)/../../cmodules/micropython.cmake \
        FROZEN_MANIFEST=$(pwd)/manifest.py

}

function ci_esp32_build_common {
    source $IDF_TOOLS_EXPORT_CMD
    make ${MAKEOPTS} -C ../../lib/micropython/mpy-cross
    make ${MAKEOPTS} -C ../../lib/micropython/ports/esp32 submodules
}

function ci_esp32_build_cmod_spiram_s2 {
    ci_esp32_build_common

    make ${MAKEOPTS} -C ports/esp32 \
2       USER_C_MODULES=$(pwd)/../../cmodules/micropython.cmake \
        FROZEN_MANIFEST=$(pwd)/../../manifest.py

    # Test building native .mpy with xtensawin architecture.
    ci_native_mpy_modules_build xtensawin

    make ${MAKEOPTS} -C ../../lib/micropython/ports/esp32 BOARD=ESP32_GENERIC BOARD_VARIANT=SPIRAM
    make ${MAKEOPTS} -C ../../lib/micropython/ports/esp32 BOARD=ESP32_GENERIC_S2
}

function ci_esp32_build_s3_c3 {
    ci_esp32_build_common

    make ${MAKEOPTS} -C ../../lib/micropython/ports/esp32 BOARD=ESP32_GENERIC_S3
    make ${MAKEOPTS} -C ../../lib/micropython/ports/esp32 BOARD=ESP32_GENERIC_C3
}

function ci_esp32_build_s3 {
    ci_esp32_build_common
    echo $MAKEOPTS
    make ${MAKEOPTS} -C ../../lib/micropython/ports/esp32 BOARD=ESP32_GENERIC_S3 \
        USER_C_MODULES=$(pwd)/../../cmodules/micropython.cmake \
        FROZEN_MANIFEST=$(pwd)/../../manifest.py
}
