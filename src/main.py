import machine
import onewire
import ds18x20
from machine import Pin, I2C, SoftSPI 
import time
import json
from umqtt.simple import MQTTClient
from ads1x15 import ADS1115  # Assuming you have the ads1x15 library by Robert H.H.
import ssd1306
# import lcd_i2c


# Constants
MQTT_BROKER = '192.168.1.4'  # Replace with your MQTT server address
MQTT_CLIENT_ID = 'kaffemaskin_temperature_pressure_sensor'
# MQTT_DISCOVERY_TOPIC = 'homeassistant/sensor/coffeemaker-monitor/{}/config'
MQTT_SENSOR_TOPIC = 'wega/{}/{}'
MQTT_CMD_TOPIC = 'wega/cmd'
MAX_RETRIES = 5  # Number of retries before failing
#<discovery_prefix>/<component>/[<node_id>/]<object_id>/config

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

print(ads)


# Function to connect to MQTT server
def connect_mqtt(unique_id):
    # Initialize MQTT client
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER)
    # Set callback function
    client.set_callback(mqtt_callback)
    while True:
        try:
            client.connect()
            print('Connected to MQTT broker')
            
            # Subscribe to the command topic
            client.subscribe(MQTT_CMD_TOPIC)
            print(f"Subscribed to {MQTT_CMD_TOPIC}")
            
            client.set_callback(mqtt_disconnect_callback)
            # publish_discovery_payload(client, unique_id, version)

            return client
        except OSError as e:
            print('Failed to connect to MQTT broker. Retrying...', e)
            time.sleep(5)

# Function to handle MQTT disconnection
def mqtt_disconnect_callback(client):
    print('Disconnected from MQTT broker. Reconnecting...')

# Callback function to handle incoming MQTT messages
def mqtt_callback(topic, msg):
    print(f"Received message on topic {topic}: {msg}")

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

with open("version.txt", "r") as file:
    version = file.read().strip()

print(version)

def publish_discovery_payload(client, unique_id, version):
    if client is None or unique_id is None:
        return

    # Common device information for Home Assistant discovery
    temp_cfg = {
        "state_topic": MQTT_SENSOR_TOPIC.format(unique_id, "temperature"),
        "icon": "hass:thermometer",
        "name": "Boiler Temperature",
        "unique_id": f"wega_{unique_id}_temperature",
        "device": {
            "identifiers": [
                f"coffeemaker_{unique_id}"
            ],
            "manufacturer": "Wega",
            "model": "Polaris",
            "name": "coffeemaker",
            "sw": version,
        },
        "unit_of_measurement": "°C",
        "device_class": "temperature",
        "state_class": "measurement"
    }

    press_cfg = {
        "state_topic": MQTT_SENSOR_TOPIC.format(unique_id, "pressure"),
        "icon": "hass:gauge",
        "name": "Boiler Pressure",
        "unique_id": f"wega_{unique_id}_pressure",
        "device": {
            "identifiers": [
                f"coffeemaker_{unique_id}"
            ],
            "manufacturer": "Wega",
            "model": "Polaris",
            "name": "coffeemaker",
            "sw": version,
        },
        "unit_of_measurement": "bar",
        "device_class": "pressure",
        "state_class": "measurement"
    }

    cfg = {
        "device": {
            "ids": {unique_id},
            "name": "Coffeemachine",
            "mf": "Wega",
            "mdl": "Polaris",
            "sw": version,
        },
        "origin": {
            "name":"esp-temp-and-pressure",
            "sw": version,
            "url": "https://github.com/stenjo/esp-temp-and-pressure"
        },
        "components": {
            "boiler_temperature": {
                "platform": "sensor",
                "device_class":"temperature",
                "unit_of_measurement":"°C",
                "value_template":"{{ value_json.temperature}}",
                "unique_id":f"wega_{unique_id}_t"
            },
            "boiler_pressure": {
                "platform": "sensor",
                "device_class":"pressure",
                "unit_of_measurement":"bar",
                "value_template":"{{ value_json.pressure}}",
                "unique_id":f"wega_{unique_id}_p"
            }
        },
        "state_topic":"wega/state",
        "qos": 2
    }

    DISCOVERY_TOPIC = 'homeassistant/device/wega_{}/config'


    try:

        # Convert to JSON string
        temp_payload_str = json.dumps(temp_cfg)
        # print("Discovery Payload Temp JSON:", temp_payload_str)
        # client.publish(MQTT_DISCOVERY_TOPIC.format(unique_id, "temperature"), temp_cfg, retain=True)

        press_payload_str = json.dumps(press_cfg)
        # Debug: Print JSON string to confirm structure
        # print("Discovery Payload Press JSON:", press_payload_str)
        # client.publish(MQTT_DISCOVERY_TOPIC.format(unique_id, "pressure"), press_cfg, retain=True)

        # Publish the discovery payload
        discovery_payload_str = json.dumps(cfg)
        print("Discovery Config Payload JSON:", discovery_payload_str)

        client.publish(DISCOVERY_TOPIC.format(unique_id), discovery_payload_str, retain=True)
        
        print('Published discovery payloads for temperature and pressure sensors')

    except OSError as e:
        print(f"JSON encoding error: {e}")

# Main function
def main():
    temp, rom = read_temperature_with_retries()
    pressure = 0
    client = None
    if rom is not None:
        unique_id = ''.join('{:02x}'.format(x) for x in rom)[:5]
    
        try:
            client = connect_mqtt(unique_id)
            publish_discovery_payload(client, unique_id, version)
        except ConnectionError as e:
            print("Failed connecting: ", e)

        while True:

            if not client:
                try:
                    client = connect_mqtt(unique_id)
                    if pressure == 0:
                        publish_discovery_payload(client, unique_id, version)
                except ConnectionError as e:
                    print("Failed connecting: ", e)


            try:
                temp, _ = read_temperature_with_retries()
            except IOError as e:
                print("Failed reading sensors:", e)
            
            value_type = None
            sensor_value = None

            if temp is not None:
                sensor_value = round(temp,1)
                value_type = "temperature"
            try:
                topic = MQTT_SENSOR_TOPIC.format(unique_id, value_type);
                client.publish(topic, f"{sensor_value}")
                print('Published sensor data:', topic, f"{sensor_value}")

            except OSError as e:
                print('Failed to publish sensor data. Reconnecting...', e)
                client = None
                continue

            # Limit wait_msg to 5 seconds
            start_time = time.time()
            while time.time() - start_time < 5:
                # client.check_msg()  # Check for a message and call the callback function if a message is received
                time.sleep(0.5)  # Sleep for a short interval to avoid busy-waiting

            try:
                pressure = round((read_pressure() - 2600)/2000, 2)
            except OSError as e:
                print("Failed reading sensors:", e)

            if pressure is not None:
                sensor_value = pressure
                value_type = "pressure"
            try:
                topic = MQTT_SENSOR_TOPIC.format(unique_id[:5], value_type)
                client.publish(topic, f"{sensor_value}")
                print('Published sensor data:', topic,  f"{sensor_value}")

            except OSError as e:
                print('Failed to publish sensor data. Reconnecting...', e)
                client = None
                continue
        
            # Limit wait_msg to 5 seconds
            start_time = time.time()
            while time.time() - start_time < 5:
                # client.check_msg()  # Check for a message and call the callback function if a message is received
                time.sleep(0.5)  # Sleep for a short interval to avoid busy-waiting


if __name__ == "__main__":
    main()