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
    if debug:
        print('WiFi Activated')
    wlan.connect(ssid, password)
    attempts = 10
    if debug:
        print('Link ', end='')
    while wlan.isconnected() == False:
        if debug:
            print('.', end='')
        # LED option to blink while connecting to WiFi
        led.off()
        sleep(.5)
        led.on()
        sleep(.5)
        attempts = attempts -1
        if attempts == 0:
            if debug:
                print('failed')
            return 0
    if debug:
        print('acquired')
    return wlan.ifconfig()[0]

def report(server, time, temp, humi):
    # Report Temp Humidity and Time to MQTT
    c = MQTTClient("Pico_1", server)
    try:
        c.connect()
        c.publish(b"sensor/temperature", temp)
        c.publish(b"sensor/humidity", humi)
        c.publish(b"sensor/time", time)
        c.disconnect()
    except:
        if debug:
            print('Could not connect to MQTT server')          


# Set up LED to turn it on while active, off when sleeping
led = Pin("LED", Pin.OUT)
# Set i2c unit, SCL pin and SDA pin for AHT21 module on Pi Pico
i2c = machine.I2C(id=0, scl=machine.Pin(1), sda=machine.Pin(0))
sensor = aht.AHT2x(i2c, crc=True)
# set up wlan here so we can power it down in the main loop
wlan = network.WLAN(network.STA_IF)


#Main Loop
while True:
    # LED option to turn on when working, off when sleeping
    led.on()
    sensor.reset
    sleep(4) # this is here so it's easier to interrupt the main.py program that runs automatically.
    ip=connect()
    if wlan.isconnected():
        if debug:
            print(f'Connected on {wlan.ifconfig()}')
        #ntptime.settime(UTC_offset, ntp_host)
        try:
            ntptime.settime()    
        except:
            if debug:
                print('Could not get time from NTP server')
        timeobj=time.localtime()
        asctime = '{}:{}:{}:{}:{}:{}'.format(*timeobj)
        if debug:
            print(asctime)
        humi = '{:.0f}'.format(sensor.humidity)    
        if debug:
            print("Humidity: " + humi + "%")
        temp = sensor.temperature
        tempc = '{:.1f}'.format(temp)
        tempf = '{:.1f}'.format(temp / 5 * 9 + 32)
        if debug:
            print("Temperature C: " + tempc)
            print("Temperature F: " + tempf)
        report(mqtt_host, asctime, tempf, humi)
    else:
        if debug:
            print('No IP connection, sleep and try again')
    #try:
    wlan.deinit()  #This turns off the WiFi Radio while Pico sleeps
    # turn off LED when sleeping
    led.off()
    machine.lightsleep(int(test_interval * 60000))  #Light Sleep is a lower power mode than "sleep"
    if debug:
        sleep(2) # Allow the USB to re-establish so we can print again. 
        print(f"Waking Up from {test_interval} minutes sleep")

