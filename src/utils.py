import network
from wifi_setup.wifi_setup import WiFiSetup
import time


def show_ip_and_version(matrix):
    # Get version
    sta_if = network.WLAN(network.STA_IF)
    filename = "version.txt"
    f = open(filename, "r")
    version = f.read().replace("\n", "")
    matrix.marquee(sta_if.ifconfig()[0] + " " + version)
    while not matrix.scroll():
        pass

def reconnectIfNotConnected():
    sta_if = network.WLAN(network.STA_IF); sta_if.active(True)
    if not sta_if.isconnected():
        while not sta_if.isconnected():
            sta_if.active(True)
            print("Trying to connect...")
            time.delay(1)
        ws = WiFiSetup("dot-matrix-calendar")
        sta = ws.connect_or_setup()
        del ws