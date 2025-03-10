import machine
import onewire
import ds18x20
from machine import Pin, I2C, SoftSPI 
import time
import json
from umqtt.simple import MQTTClient
from ads1x15 import ADS1115  # Assuming you have the ads1x15 library by Robert H.H.
import ssd1306
import lcd_i2c


# Constants
MQTT_BROKER = '192.168.1.4'  # Replace with your MQTT server address
MQTT_CLIENT_ID = 'kaffemaskin_temperature_pressure_sensor'
MQTT_DISCOVERY_TOPIC = 'homeassistant/sensor/{}/config'
MQTT_SENSOR_TOPIC = 'homeassistant/sensor/{}/state'
MAX_RETRIES = 5  # Number of retries before failing

# PCF8574 on 0x50
I2C_ADDR = 0x27     # DEC 39, HEX 0x27
NUM_ROWS = 2
NUM_COLS = 16

# import captive
# captive.start()

# Pins:
# 0 SPI miso
# 1 REPL UART TX
# 2 SPI cs
# 3 REPL UART RX
# 4 ds_pin
# 5 SPI dc
# 12 I2C sda
# 13 SPI mosi
# 14 I2C slc
# 15 SPI sck
# 16 WAKEUP SPI rst

# Setup OneWire and DS18x20
ds_pin = machine.Pin(4)  # Use the correct pin for your setup (D2 on ESP8266 is GPIO4)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))

# Setup I2C for BMP280
i2c = machine.I2C(scl=machine.Pin(14), sda=machine.Pin(12))  # Adjust pins as needed
ads = ADS1115(i2c)

# Setup SPI for display
sck=Pin(15, Pin.OUT)
mosi=Pin(13, Pin.OUT) 
miso=Pin(0, Pin.IN)
spi = SoftSPI(baudrate=50000, polarity=1, phase=0, sck=sck, mosi=mosi, miso=miso)

dc = Pin(5, Pin.OUT)   # data/command
rst = Pin(16, Pin.OUT)  # reset
cs = Pin(2, Pin.OUT)  # chip select, some modules do not have a pin for this

display = ssd1306.SSD1306_SPI(128, 64, spi, dc, rst, cs)

# display.fill(0)
# display.fill_rect(0, 0, 32, 32, 1)
# display.fill_rect(2, 2, 28, 28, 0)
# display.vline(9, 8, 22, 1)
# display.vline(16, 2, 22, 1)
# display.vline(23, 8, 22, 1)
# display.fill_rect(26, 24, 2, 4, 1)
# display.text('MicroPython', 40, 0, 1)
# display.text('SSD1306', 40, 12, 1)
# display.text('OLED 128x64', 40, 24, 1)
# display.show()

lcd = LCD(addr=I2C_ADDR, cols=NUM_COLS, rows=NUM_ROWS, i2c=i2c)

lcd.begin()
lcd.print("Hello World")

print(ads)

# Function to connect to MQTT server
def connect_mqtt():
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER)
    while True:
        try:
            client.connect()
            print('Connected to MQTT broker')
            return client
        except OSError as e:
            print('Failed to connect to MQTT broker. Retrying...')
            time.sleep(5)

# Function to handle MQTT disconnection
def mqtt_disconnect_callback(client):
    print('Disconnected from MQTT broker. Reconnecting...')
    connect_mqtt()

# Function to read temperature from DS18x20 sensor
def read_temperature():
    roms = ds_sensor.scan()
    if roms is None: return None
    ds_sensor.convert_temp()
    time.sleep_ms(750)  # Wait for temperature conversion
    for rom in roms:
        try:
            temp = ds_sensor.read_temp(rom)
            return temp, rom
        except:
            return None, None

def read_temperature_with_retries():
    retries = 0
    while retries < MAX_RETRIES:
        temp, rom = read_temperature()
        if temp is not None and rom is not None:
            return temp, rom
        retries += 1
        time.sleep(1)
    return None, None

# Function to read pressure from ADS1115 sensor
def read_pressure():
    try:
        # Read the analog value from the ADS1115 (assuming single-ended mode on channel 0)
        pressure = ads.read(0)
        return pressure
    except OSError as e:
        print('Failed to read pressure sensor')
        return None

import json

def publish_discovery_payload(client, unique_id):
    # Common device information for Home Assistant discovery
    device_info = {
        "identifiers": [unique_id],
        "name": "Kaffemaskin Sensor Device",
        "model": "Kaffemaskin Model 1",
        "manufacturer": "Kaffemaskin Inc"
    }

    # Temperature sensor payload with direct value_template
    temperature_payload = {
        "name": f"Kaffemaskin Temperature Sensor {unique_id}",
        "state_topic": MQTT_SENSOR_TOPIC.format(unique_id),
        "unit_of_measurement": "°C",
        "value_template": "{{ value_json.temperature }}",  # Standard template without additional tags
        "device_class": "temperature",
        "unique_id": f"{unique_id}_temperature",
        "device": device_info
    }

    # Pressure sensor payload with direct value_template
    pressure_payload = {
        "name": f"Kaffemaskin Pressure Sensor {unique_id}",
        "state_topic": MQTT_SENSOR_TOPIC.format(unique_id),
        "unit_of_measurement": "bar",
        "value_template": "{{ value_json.pressure }}",  # Standard template without additional tags
        "device_class": "pressure",
        "unique_id": f"{unique_id}_pressure",
        "device": device_info
    }

    try:
        # Convert to JSON strings explicitly
        temperature_payload_str = json.dumps(temperature_payload)
        pressure_payload_str = json.dumps(pressure_payload)

        # Debug: Print JSON strings to confirm structure
        print("Temperature Payload JSON:", temperature_payload_str)
        print("Pressure Payload JSON:", pressure_payload_str)

        # Publish both discovery payloads
        client.publish(MQTT_DISCOVERY_TOPIC.format(unique_id + "_temperature"), temperature_payload_str, retain=True)
        client.publish(MQTT_DISCOVERY_TOPIC.format(unique_id + "_pressure"), pressure_payload_str, retain=True)
        
        print('Published discovery payloads for temperature and pressure sensors')

    except json.JSONDecodeError as e:
        print(f"JSON encoding error: {e}")

# Main function
def main():
    client = connect_mqtt()
    client.set_callback(mqtt_disconnect_callback)
    temp, rom = read_temperature_with_retries()
    pressure = 0
    if rom is not None:
        unique_id = ''.join('{:02x}'.format(x) for x in rom)
        publish_discovery_payload(client, unique_id)
    
        while True:
            try:
                temp, _ = read_temperature_with_retries()
                pressure = round((read_pressure() - 2600)/2000, 2)
            except:
                pass
            if temp is not None or pressure is not None:
                sensor_payload = {}
                if temp is not None:
                    sensor_payload["temperature"] = round(temp,1)
                if pressure is not None:
                    sensor_payload["pressure"] = pressure
                try:
                    client.publish(MQTT_SENSOR_TOPIC.format(unique_id), json.dumps(sensor_payload))
                    print('Published sensor data:', sensor_payload)
                    display.text("temp", 0, 0, 1)
                    display.show()
                except OSError as e:
                    print('Failed to publish sensor data. Reconnecting...')
                    client = connect_mqtt()
            time.sleep(5)  # Adjust the sleep time as needed

if __name__ == "__main__":
    main()