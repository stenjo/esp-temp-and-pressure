import time
import machine
import onewire
import ds18x20
import network
from umqtt.simple import MQTTClient

# Configuration for the MQTT server
MQTT_BROKER = 'mqtt.example.com'  # Replace with your MQTT server address
MQTT_TOPIC = 'sensor/temperature'
MQTT_CLIENT_ID = 'esp8266_temperature_sensor'

# WiFi credentials
WIFI_SSID = 'your_wifi_ssid'
WIFI_PASSWORD = 'your_wifi_password'

# GPIO pin where the DS18x20 is connected
ds_pin = machine.Pin(4)  # Use the correct pin for your setup (D2 on ESP8266 is GPIO4)

# Setup OneWire and DS18x20
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))

# Function to connect to Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to network...')
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            time.sleep(1)
    print('Connected to WiFi:', wlan.ifconfig())

# Function to connect to MQTT server
def connect_mqtt():
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER)
    client.connect()
    print('Connected to MQTT broker')
    return client

# Function to read temperature from DS18x20 sensor
def read_temperature():
    roms = ds_sensor.scan()
    ds_sensor.convert_temp()
    time.sleep_ms(750)  # Wait for temperature conversion
    for rom in roms:
        temp = ds_sensor.read_temp(rom)
        return temp

# Main function
def main():
    connect_wifi()
    client = connect_mqtt()

    while True:
        temp = read_temperature()
        if temp is not None:
            print('Temperature: {:.2f}°C'.format(temp))
            client.publish(MQTT_TOPIC, str(temp))  # Publish temperature to MQTT
        else:
            print('Failed to read temperature')
        
        time.sleep(5)  # Wait 5 seconds before reading again

# Run the main function
if __name__ == '__main__':
    main()
