import machine
import onewire
import ds18x20
import time
import json
from umqtt.simple import MQTTClient
from ads1x15 import ADS1115  # Assuming you have the ads1x15 library by Robert H.H.

# Constants
MQTT_BROKER = '192.168.1.4'  # Replace with your MQTT server address
MQTT_CLIENT_ID = 'kaffemaskin_temperature_pressure_sensor'
MQTT_DISCOVERY_TOPIC = 'homeassistant/sensor/{}/config'
MQTT_SENSOR_TOPIC = 'homeassistant/sensor/{}/state'
MAX_RETRIES = 5  # Number of retries before failing


# import captive
# captive.start()

# GPIO pin where the DS18x20 is connected
ds_pin = machine.Pin(14)  # Use the correct pin for your setup (D2 on ESP8266 is GPIO4)

# Setup OneWire and DS18x20
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))

# Setup I2C for BMP280
i2c = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4))  # Adjust pins as needed
ads = ADS1115(i2c)

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
    ds_sensor.convert_temp()
    time.sleep_ms(750)  # Wait for temperature conversion
    for rom in roms:
        try:
            temp = ds_sensor.read_temp(rom)
            return temp, rom
        except OSError as e:
            return None


def read_temperature_with_retries():
    retries = 0
    while retries < MAX_RETRIES:
        temp, rom = read_temperature()
        if temp is not None:
            return temp, rom
        retries += 1
        time.sleep(1)
    return None, None

# Function to read pressure from ADS1115 sensor
def read_pressure():
    try:
        # Read the analog value from the ADS1115 (assuming single-ended mode on channel 0)
        value = ads.read(0)
        # Convert the analog value to pressure (this conversion depends on your specific sensor)
        pressure = value * 0.125  # Example conversion factor
        return pressure
    except OSError as e:
        print('Failed to read pressure sensor')
        return None

# Function to publish discovery payload
def publish_discovery_payload(client, unique_id):
    discovery_payload = {
        "name": f"Kaffemaskin Sensor {unique_id}",
        "state_topic": MQTT_SENSOR_TOPIC.format(unique_id),
        "unit_of_measurement": "°C",
        "value_template": "{{ value_json.temperature }}",
        "device_class": "temperature",
        "unique_id": unique_id
    }
    client.publish(MQTT_DISCOVERY_TOPIC.format(unique_id), json.dumps(discovery_payload), retain=True)
    print('Published discovery payload')

# Main function
def main():
    client = connect_mqtt()
    client.set_callback(mqtt_disconnect_callback)
    temp, rom = read_temperature_with_retries()
    if rom is not None:
        unique_id = ''.join('{:02x}'.format(x) for x in rom)
        publish_discovery_payload(client, unique_id)
    
        while True:
            temp, _ = read_temperature_with_retries()
            pressure = read_pressure()
            if temp is not None or pressure is not None:
                sensor_payload = {}
                if temp is not None:
                    sensor_payload["temperature"] = temp
                if pressure is not None:
                    sensor_payload["pressure"] = pressure
                try:
                    client.publish(MQTT_SENSOR_TOPIC.format(unique_id), json.dumps(sensor_payload))
                    print('Published sensor data:', sensor_payload)
                except OSError as e:
                    print('Failed to publish sensor data. Reconnecting...')
                    client = connect_mqtt()
            time.sleep(10)  # Adjust the sleep time as needed

if __name__ == "__main__":
    main()