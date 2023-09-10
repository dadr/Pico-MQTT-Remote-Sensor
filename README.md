# Introduction

This is a simple MicroPython program designed to spend most of its time in a low power sleep mode,
then periodically:
- wake up, 
- connect to Wi-Fi, 
- set the time from an NTP server, 
- take temperature and humidity measurements using an AHT20 or AHT21 sensor
- Connect to a MQTT server and report measurements and time
- turn off the Wi-Fi
- go back to sleep


# Dependencies

Written for Raspberry Pi Pico W, using AHT20 or AHT21 sensors.

MicroPython version 1.20.0

This program makes use of aht.py in order to take measurements from the sensor.
aht.py info is in a separate directory 
and can also be referenced from https://github.com/etno712/aht


# Install


## Hardware:

AHT2x sensor connects to the Pi Pico as Follows:
```
AHT Pin  	Pico Pin
VIN  ---------- 36 (3V3(OUT))
GND  ---------- 38 (GND)
SCL  ----------  2 (I2C0 SCL)
SDA  ----------  1 (I2C0 SDA)
```
_________

## Software:

Open main.py in your python editor and set the Configuration Data variables for your environment

Copy the files main.py and aht.py in your project folder and save to the Pico.

You can test-run the program from Thonny console, but cannot interrupt the program while it is sleeping.  Hit Stop when the LED is on.

For a MQTT client on another system, the messages to subscribe to are `/sensor/temperature, /sensor/humidity`, and `/sensor/time`.

For example, on a server running a Mosquitto MQTT broker, the following example shows a CLI that subscribes verbosely to all the messages:

```
user@server:~$ mosquitto_sub -v -h localhost -t "sensor/+"
sensor/temperature 80.0233
sensor/humidity 47.95837
sensor/time 2023:9:9:23:4:19
```

The program is easily edited to return temp in C or F.  The sensor returns C, and there is a step to convert to F which can be deleted if desired.


# Contributing

Other than trying the introductory programs, this is my first MicroPython program on a Pico W.

So inputs and Contributions are welcome!
