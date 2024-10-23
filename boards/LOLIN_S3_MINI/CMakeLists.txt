cmake_minimum_required(VERSION 3.12)
add_definitions(-DESP32)

# Set the location of MicroPython, the esp32 port, and the board directory.
get_filename_component(PROJECT_DIR "../.." ABSOLUTE)
#get_filename_component(MICROPY_TOP "../../lib/micropython" ABSOLUTE)
# set(MICROPY_PORT_DIR ${MICROPY_TOP}/ports/esp32)
set(MICROPY_PORT_DIR ${PROJECT_DIR}/lib/micropython/ports/esp32)
get_filename_component(MICROPY_BOARD_DIR "." ABSOLUTE)

# Define the output sdkconfig so it goes in the build directory.
set(SDKCONFIG ${CMAKE_BINARY_DIR}/sdkconfig)

# Include board config; this is expected to set SDKCONFIG_DEFAULTS (among other options).
include(${MICROPY_BOARD_DIR}/mpconfigboard.cmake)

# Concatenate all sdkconfig files into a combined one for the IDF to use.
file(WRITE ${CMAKE_BINARY_DIR}/sdkconfig.combined.in "")
foreach(SDKCONFIG_DEFAULT ${SDKCONFIG_DEFAULTS})
    file(READ ${SDKCONFIG_DEFAULT} CONTENTS)
    file(APPEND ${CMAKE_BINARY_DIR}/sdkconfig.combined.in "${CONTENTS}")
endforeach()

file(READ sdkconfig.board CONTENTS)
file(APPEND ${CMAKE_BINARY_DIR}/sdkconfig.combined.in "${CONTENTS}")

configure_file(${CMAKE_BINARY_DIR}/sdkconfig.combined.in ${CMAKE_BINARY_DIR}/sdkconfig.combined COPYONLY)
set(SDKCONFIG_DEFAULTS ${CMAKE_BINARY_DIR}/sdkconfig.combined)

# Include main IDF cmake file and define the project.
include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(micropython)

# # Set location of base MicroPython directory.
# # set(MICROPY_DIR ${PROJECT_DIR}/../../lib/micropython/ ABSOLUTE)
# if(NOT MICROPY_DIR)
#     get_filename_component(MICROPY_DIR ${CMAKE_CURRENT_LIST_DIR}/../.. ABSOLUTE)
# endif()

# # Set location of the ESP32 port directory.
# if(NOT MICROPY_PORT_DIR)
#     get_filename_component(MICROPY_PORT_DIR ${MICROPY_DIR}/ports/esp32 ABSOLUTE)
# endif()

# include(${MICROPY_PORT_DIR}/esp32_common.cmake)
