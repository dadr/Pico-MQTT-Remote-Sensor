"""
Pico MQTT Remote Sensor
Micropython program for Pico W to take periodic measurements and report them to a MQTT broker.
https://github.com/dadr/Pico-MQTT-Remote-Sensor

"""
__author__ = "Tom Anschutz"
__credits__ = ["Tom Anschutz"]
__license__ = "GPL version 3"
__version__ = "1.0"
__maintainer__ = "Tom Anschutz"

import network
import socket
import time
from time import sleep
import ntptime
import machine
from machine import Pin
from machine import I2C
from machine import lightsleep
import aht
from umqtt.simple import MQTTClient

""" ----- Configuration Data ----- """
# Time between measurements in Minutes
test_interval = 15

# NTP host defaults to "pool.ntp.org"
# ntptime.host = "custom.host.org"

# WiFi
ssid = 'SSID'
password = 'WiFi Password'

#MQTT Broker (host)
mqtt_host = "your.mqtt.host.org"
# Each sensor must have a unique client_ID. If you don't set it, a random ID gets generated.
mqtt_client_ID = "Pico_1"
# To change MQTT messages edit report function

# DEBUG Messages for Thonny Console
debug = False
""" ----- END Configuration Data ----- """


def connect():  # Connect to Wi-Fi - remove #
    #Connect to WLAN
    #wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    if debug:
        print('Connecting', end='')
    attempts = 10
    while wlan.isconnected() == False:
        if debug:
            print('.', end='')
        sleep(2)
        attempts = attempts -1
        if attempts == 0:
            return 0
    if debug:
        print('.')
    ip = wlan.ifconfig()[0]
    return ip

def report(server, time, temp, humi):
    # Report Temp Humidity and Time to MQTT
    c = MQTTClient("Pico_1", server)
    try:
        c.connect()
        c.publish(b"sensor/temperature", temp)
        c.publish(b"sensor/humidity", humi)
        c.publish(b"sensor/time", time)
    finally:    
        c.disconnect()

# Set up LED to turn it on while active, off when sleeping
led = Pin("LED", Pin.OUT)
# Set i2c unit, SCL pin and SDA pin for AHT21 module on Pi Pico
i2c = machine.I2C(id=0, scl=machine.Pin(1), sda=machine.Pin(0))
sensor = aht.AHT2x(i2c, crc=True)
# set up wlan here so we can power it down in the main loop
wlan = network.WLAN(network.STA_IF)


# Main Loop
while True:
    led.on()
    sensor.reset
    ip=connect()
    if debug:
        print(f'Connected on {ip}')
    #ntptime.settime(UTC_offset, ntp_host)
    ntptime.settime()    
    timeobj=time.localtime()
    asctime=str(timeobj[0])+':'+str(timeobj[1])+':'+str(timeobj[2])+':'+str(timeobj[3])+':'+str(timeobj[4])+':'+str(timeobj[5])
    if debug:
        print(asctime)
    humi = sensor.humidity
    if debug:
        print("Humidity: {:.2f}".format(humi))
    tempf = sensor.temperature / 5 * 9 + 32
    if debug:
        print("Temperature C: {:.2f}".format(sensor.temperature))
        print("Temperature F: {:.2f}".format(tempf))
    report(mqtt_host, asctime, str(tempf), str(sensor.humidity))
    wlan.deinit()  #This turns off the WiFi Radio while Pico sleeps
    led.off()
    machine.lightsleep(test_interval * 60000)  #Light Sleep is a lower power mode than "sleep"
    if debug:
        print(f"Waking Up from {test_interval} minutes sleep")

