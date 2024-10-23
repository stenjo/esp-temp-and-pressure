        MAKEOPTS="-j$(sysctl -n hw.ncpu)"

########################################################################################
# ports/esp8266

function ci_esp8266_setup() {
    sudo pip install pyserial esptool==3.3.1
    wget https://github.com/jepler/esp-open-sdk/releases/download/2018-06-10/xtensa-lx106-elf-standalone.tar.gz
    zcat xtensa-lx106-elf-standalone.tar.gz | tar x
    # Remove this esptool.py so pip version is used instead
    rm xtensa-lx106-elf/bin/esptool.py
}

function ci_esp8266_path() {
    echo $(pwd)/xtensa-lx106-elf/bin
}

function ci_esp8266_build() {
    docker run --rm -v $HOME:$HOME -u $UID -w $PWD larsks/esp-open-sdk make PYTHON=python3 ${MAKEOPTS} -C ../../lib/micropython/mpy-cross
    docker run --rm -v $HOME:$HOME -u $UID -w $PWD larsks/esp-open-sdk make PYTHON=python3 ${MAKEOPTS} -C ../../lib/micropython/ports/esp8266 submodules
    docker run --rm -v $HOME:$HOME -u $UID -w $PWD larsks/esp-open-sdk make PYTHON=python3 ${MAKEOPTS} -C ../../lib/micropython/ports/esp8266 BOARD=ESP8266_GENERIC
    docker run --rm -v $HOME:$HOME -u $UID -w $PWD larsks/esp-open-sdk make PYTHON=python3 ${MAKEOPTS} -C ../../lib/micropython/ports/esp8266 BOARD=ESP8266_GENERIC BOARD_VARIANT=FLASH_512K
    docker run --rm -v $HOME:$HOME -u $UID -w $PWD larsks/esp-open-sdk make PYTHON=python3 ${MAKEOPTS} -C ../../lib/micropython/ports/esp8266 BOARD=ESP8266_GENERIC BOARD_VARIANT=FLASH_1M
    docker run --rm -v $HOME:$HOME -u $UID -w $PWD larsks/esp-open-sdk make PYTHON=python3 ${MAKEOPTS} BOARD=ESP8266_GENERIC
}

"$@"