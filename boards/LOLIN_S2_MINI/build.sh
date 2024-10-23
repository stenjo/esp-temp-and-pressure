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