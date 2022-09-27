#! /usr/bin/env python
#  -*- coding: utf-8 -*-
#
# This file is part of dogratian_usb_sensors module

__intname__ = "usb_dogratian_sensors_tests"
__author__ = "Orsiris de Jong"
__copyright__ = "Copyright (C) 2022 Orsiris de Jong"
__licence__ = "BSD 3 Clause"
__build__ = "2022092701"


import os
import sys
from time import sleep

try:
    from dogratian_usb_sensors import USBSensor
except ImportError:  # in python 3+ it would be ModuleNotFoundError
    # In case we run tests without actually having installed the module, let's try to add it
    sys.path.insert(0, os.path.abspath(os.path.join(__file__, os.pardir, os.pardir)))
    from dogratian_usb_sensors import USBSensor


def test_usb_sensors():
    sensor_ports = USBSensor.find_sensors()
    if not sensor_ports:
        print("No sensors found")
    for sensor_port in sensor_ports:
        print("Found sensor at port {}".format(sensor_port))
        sensor = USBSensor(sensor_port, state_led=False)
        model = sensor.model
        count = 0
        try:
            while count < 5:
                if model in ["USB-TnH", "USB-PA"]:
                    temperature = sensor.temperature
                    humidity = sensor.humidity
                    print("Current temperature: {} °C".format(temperature))
                    print("Current humidity: {} %".format(humidity))
                    assert isinstance(
                        temperature, float
                    ), "Temperature should be a float"
                    assert isinstance(humidity, float), "Humidity should be a float"
                if sensor.model == "USB-PA":
                    pressure = sensor.pressure
                    print("Current pressure: {} %".format(pressure))
                    assert isinstance(pressure, float), "Pressure should be a float"
                if sensor.model not in ["USB-TnH", "USB-PA"]:
                    result = sensor.all
                    print("Readings: {}".format(result))
                    for element in result:
                        assert isinstance(
                            result[element], float
                        ), "Result should only contain floats"
                sleep(0.1)
                count += 1
                if count == 2:
                    sensor.led = True
                if count == 3:
                    sensor.led = False
        except PermissionError as exc:
            print(
                "We don't have permission to use serial ports: {}. This can also happen if port is already open.".format(
                    exc
                )
            )


if __name__ == "__main__":
    test_usb_sensors()
