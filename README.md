# DogRatIan USB-TnH, USB-PA and USB-VOC python lib

This library makes usage of https://www.dogratian.com sensors easy

[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Percentage of issues still open](http://isitmaintained.com/badge/open/netinvent/usb_sensors.svg)](http://isitmaintained.com/project/netinvent/usb_sensors "Percentage of issues still open")
[![linux-tests](https://github.com/netinvent/usb_sensors/actions/workflows/linux.yaml/badge.svg)](https://github.com/netinvent/usb_sensors/actions/workflows/linux.yaml)
[![windows-tests](https://github.com/netinvent/usb_sensors/actions/workflows/windows.yaml/badge.svg)](https://github.com/netinvent/usb_sensors/actions/workflows/windows.yaml)
[![GitHub Release](https://img.shields.io/github/release/netinvent/usb_sensors.svg?label=Latest)](https://github.com/netinvent/usb_sensors/releases/latest)

Setup:
`pip install dogratian_usb_sensors`  # Future if DogRatIan agrees 

Quick Usage:
```python
from dogratian_usb_sensors import USBSensor

# Returns serial port names for every connected DogRatIan device
sensor_ports = USBSensor.find_sensors()

# Read data for every sensor on system
for sensor_port in sensor_ports:
    sensor = USBSensor(sensor_port)
    print(sensor.model)
    print(sensor.version)
    print(sensor.temperature)       # Only on USB-PA and USB-TnH sensors
    print(sensor.humidity)          # Only on USB-PA and USB-TnH sensors
    print(sensor.name)
    print(sensor.pressure)          # Only on USB-PA sensor
    print(sensor.voc)               # Only on USB-VOC sensor
    print(sensor.co2eq)             # Only on USB-VOC sensor
    print(sensor.identification)
```

Reading all possible measurement values from a sensor
```python
for sensor_port in USBSensor.find_sensors():
    sensor = USBSensor(sensor_port)
    print(sensor.all)
```

# Sensor differences

DogRatIan uses USB-TnH (temperature and humidity), USB-PA (temperature, humidity and atmospheric pressure) as well as USB-VOC (volatile organic compounds) sensors.
All three sensors are returned by `USBSensor.find_sensors()`.

Depending on the sensor you have, not all commands will run.
You can identify a sensor by using `sensor.model` property.

# Basic usage

```python
from time import sleep
from dogratian_usb_sensors import USBSensor

sensor_ports = USBSensor.find_sensors()

for sensor_port in sensor_ports:
    print("Found sensor at port {}".format(sensor_port))
    sensor = USBSensor(sensor_port, state_led=True)
    print("Sensor model is {}".format(sensor.model))

    count = 0
    while count < 10:
        print("Current temperature: {}".format(sensor.temperature))
        print("Current humidity: {}".format(sensor.humidity))
        sleep(.1)
        count += 1

```
# Writing data to the sensor

As DogRatIan suggests, you can set Name sensor to a max 8 char string, and turn on/off led.
The light will always flash when data is read on the sensor, regarless if it has been turned off.
USBSensor class has write methods implemented as setter properties, eg:

```python
from dogratian_usb_sensors import USBSensor

sensor = USBSensor('/dev/ttyUSB2')
sensor.name = 'MYSENSOR'
sensor.led = True
# Some code
sensor.led = False
```

# State led
By default, DogRatIan sensors will turn on their standby light when plugged in.
USBSensor will disable the standby light by default, unless initialized with 
Optionally, we can automatically enable the led indicator while reading with `state_led=True`.

```python
from dogratian_usb_sensors import USBSensor

sensor = USBSensor('COM4', state_led=True)
print(sensor.name)  # Light flashes while reading value
```

# Error handling

USBSensor class will raise two types of exceptions:
- ValueError when invalid opcode is given to sensor
- OSError when serial communication fails (most time you need to be root/administrator to have permissions over serial ports, and ports must not already been open by another application)