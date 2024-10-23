#define MICROPY_HW_MCU_NAME                 "ESP32-S3FH4R2"
#define MICROPY_PY_NETWORK_HOSTNAME_DEFAULT "mpy-s3-mini"

#define MICROPY_PY_BLUETOOTH                (0)
#define MICROPY_HW_ENABLE_SDCARD            (0)

#define MICROPY_HW_SPI1_MOSI                (11)
#define MICROPY_HW_SPI1_MISO                (13)
#define MICROPY_HW_SPI1_SCK                 (12)
#define MICROPY_HW_SPI1_CS                  (10)
#define MICROPY_HW_SPI_HOST                 SPI1_HOST


// Enable UART REPL for modules that have an external USB-UART and don't use native USB.
#define MICROPY_HW_ENABLE_UART_REPL         (0)

#define MICROPY_HW_I2C0_SCL                 (9)
#define MICROPY_HW_I2C0_SDA                 (8)

#define TEST_WIFI_AUTH_MAX                  (13)