from machine import SPI, Pin

spi = SPI(1, baudrate=40000)           # Create SPI peripheral 0 at frequency of 400kHz.
                                        # Depending on the use case, extra parameters may be required
                                        # to select the bus characteristics and/or pins to use.
cs = Pin(10, mode=Pin.OUT, value=1)      # Create chip-select on pin 4.
try:
    while True:
        try:
            cs(0)                               # Select peripheral.
            spi.write(b"12345678")              # Write 8 bytes, and don't care about received data.
        finally:
            cs(1)                               # Deselect peripheral.

        try:
            cs(0)                               # Select peripheral.
            rxdata = spi.read(8, 0x42)          # Read 8 bytes while writing 0x42 for each byte.
        finally:
            cs(1)                               # Deselect peripheral.

        rxdata = bytearray(8)
        try:
            cs(0)                               # Select peripheral.
            spi.readinto(rxdata, 0x42)          # Read 8 bytes inplace while writing 0x42 for each byte.
        finally:
            cs(1)                               # Deselect peripheral.

        txdata = b"12345678"
        rxdata = bytearray(len(txdata))
        try:
            cs(0)                               # Select peripheral.
            spi.write_readinto(txdata, rxdata)  # Simultaneously write and read bytes.
        finally:
            cs(1)                               # Deselect peripheral.
except KeyboardInterrupt:
    print("\nControl-C pressed. Cleaning up and exiting.")