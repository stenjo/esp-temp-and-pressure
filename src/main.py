import machine
import onewire
import ds18x20
import time
import json
from machine import Pin, I2C, SoftSPI 
from umqtt.simple import MQTTClient
from ads1x15 import ADS1115  # Assuming you have the ads1x15 library by Robert H.H.
import micropython_ota

# Constants
MQTT_BROKER = '192.168.1.4'  # Replace with your MQTT server address
MQTT_CLIENT_ID = 'kaffemaskin_temperature_pressure_sensor'
# MQTT_DISCOVERY_TOPIC = 'homeassistant/sensor/coffeemaker-monitor/{}/config'
MQTT_SENSOR_TOPIC = 'wega/{}/state'
MQTT_CMD_TOPIC = 'wega/cmd'
MAX_RETRIES = 5  # Number of retries before failing
#<discovery_prefix>/<component>/[<node_id>/]<object_id>/config

# PCF8574 on 0x50
I2C_ADDR = 0x27     # DEC 39, HEX 0x27
NUM_ROWS = 2
NUM_COLS = 16

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

# print(ads)


# Function to connect to MQTT server
def connect_mqtt(unique_id):
    # Initialize MQTT client
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER)
    # Set callback function
    client.set_callback(mqtt_callback)
    while True:
        try:
            print('Connecting to MQTT broker...')
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
        print('Failed to read temperature sensor. retrying...', retries)

    print('Failed to read temperature sensor after multiple retries')
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

    cfg = {
        "device": {
            "identifiers": f"wega_{unique_id}",
            "name": "Coffeemachine",
            "manufacturer": "Wega",
            "model": "Polaris",
            "sw_version": version,
        },
        "origin": {
            "name":"esp-temp-and-pressure",
            "sw": version,
            "url": "https://github.com/stenjo/esp-temp-and-pressure",
        },
        "components": {
            "boiler_temperature": {
                "platform": "sensor",
                "device_class":"temperature",
                "unit_of_measurement":"\u00B0C",
                "value_template":"{{ value_json.temperature}}",
                "unique_id":f"wega_{unique_id}_t",
            },
            "boiler_pressure": {
                "platform": "sensor",
                "device_class":"pressure",
                "unit_of_measurement":"bar",
                "value_template":"{{ value_json.pressure}}",
                "unique_id":f"wega_{unique_id}_p",
            }
        },
        "state_topic":MQTT_SENSOR_TOPIC.format(unique_id),
        "qos": 2,
    }

    DISCOVERY_TOPIC = 'homeassistant/device/wega_{}/config'


    try:
        # Publish the discovery payload
        discovery_payload_str = json.dumps(cfg)
        print("Discovery Config Payload JSON:", discovery_payload_str)

        client.publish(DISCOVERY_TOPIC.format(unique_id), discovery_payload_str, retain=True)
        
        print('Published discovery payloads for temperature and pressure sensors')

    except OSError as e:
        print(f"JSON encoding error: {e}")


def publish_sensor_data(client, unique_id, temp, pressure, raw):
    try:
        topic = MQTT_SENSOR_TOPIC.format(unique_id)
        state = {}
        if temp is not None: 
            state["temperature"] = temp
        if pressure is not None: 
            state["pressure"] = pressure
            state["raw"] = raw
        client.publish(topic, json.dumps(state))
        print('Published sensor data:', topic,  state)

    except OSError as e:
        print('Failed to publish sensor data. Reconnecting...', e)
        client = None
    
    return client

# Main function
def main():
    booting = True
    watchdog = machine.WDT(timeout=60000)  # Set the watchdog timer to 60 seconds
    try:
        temp, rom = read_temperature_with_retries()
        print("Temp sensor: ", ''.join('{:02x}'.format(x) for x in rom))
    except IOError as e:
        print("Failed reading temp sensor:", e)

    pressure = 0
    client = None
    if rom is not None:
        unique_id = ''.join('{:02x}'.format(x) for x in rom)[:5]
        print("Unique ID: ", unique_id)

        try:
            print("Connecting to MQTT broker...")
            client = connect_mqtt(unique_id)
            publish_discovery_payload(client, unique_id, version)
            print("Connected to MQTT broker")
        except ConnectionError as e:
            print("Failed connecting: ", e)

        while True:

            if not client:
                try:
                    client = connect_mqtt(unique_id)
                    if booting == True:
                        publish_discovery_payload(client, unique_id, version)
                        booting = False
                except ConnectionError as e:
                    print("Failed connecting: ", e)

            try:
                temp, _ = read_temperature_with_retries()
            except OSError as e:
                print("Failed reading sensors:", e)
            
            try:
                pressure = read_pressure()
            except OSError as e:
                print("Failed reading pressure sensor:", e)
                pressure = None
                bar = None
            if temp is not None or pressure is not None:
                if pressure is not None: 
                    bar = round((pressure - 4200)/3100, 1)
                else:
                    bar = None

                if temp is not None: 
                    temp = round(temp, 1)
                client = publish_sensor_data(client, unique_id, temp, bar, pressure)

                # lcd.move_to(0, 0)
                # lcd.putstr("Temp: {} °C".format(temp))

            time.sleep(5)  # Sleep for a short interval to avoid busy-waiting
            watchdog.feed()
            check_update()
            time.sleep(5) 
            watchdog.feed()

def check_update():
    
    lines = []
    try:
        with open("update.dat") as file:
            lines = file.readlines()
    except Exception as error:
        print(error)
        pass

    password = lines[0].strip()

    micropython_ota.check_for_ota_update(
                host='http://192.168.1.2:8000',
                project='esp-temp-and-pressure',
                user='admin',
                passwd=password
            )

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nControl-C pressed. Cleaning up and exiting.")
