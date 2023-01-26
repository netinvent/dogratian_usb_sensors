#! /usr/bin/env python3
#  -*- coding: utf-8 -*-


__intname__ = "dogratian_usb_sensors"
__author__ = "Orsiris de Jong"
__copyright__ = "Copyright (C) 2022-2023 Orsiris de Jong - NetInvent SASU"
__licence__ = "BSD 3 Clause"
__version__ = "1.1.1"
__build__ = "2023012601"
__compat__ = "python2.7+"


# Python 2.7 compat fixes (missing typing)
try:
    from typing import Optional, List
except ImportError:
    pass
from logging import getLogger
import serial.tools.list_ports
import serial
import json
from threading import Lock


LOCK = Lock()

# DogRatIan USB sensor ID
USB_VID = "0x03EB"
USB_PID = "0x2310"


SERIAL_SETTINGS = {
    "baudrate": 115200,
    "bytesize": 8,
    "parity": "N",
    "stopbits": 1,
}


logger = getLogger(__name__)


class USBSensor:
    def __init__(self, port=None, state_led=False):
        # type: (str, bool) -> None
        self._port = port
        self._location = (
            None  # For easier identification purposes (eg 'mainframe room')
        )
        self._available_read_cmds = ["GI", "GV", "GN", "GJSON"]
        if self.model.startswith("USB-TnH"):
            self._available_read_cmds = ["GI", "GV", "GT", "GH", "GN", "GJSON"]
        elif self.model.startswith("USB-PA"):
            self._available_read_cmds = ["GI", "GV", "GT", "GH", "GP", "GN", "GJSON"]
        elif self.model.startswith("USB-VOC"):
            self._available_read_cmds = ["GI", "GV", "GVOC", "GCO2", "GN", "GJSON"]

        self._available_write_cmds = ["I", "N"]
        self._json_map_table = {
            "T": "temperature",
            "H": "humidity",
            "P": "pressure",
            "TVOC": "tvoc",
            "CO2eq": "co2eq",
        }

        # Let's set the LED status once the sensor is initialized properly
        self.led = state_led

    @property
    def port(self):
        # type:  () -> str
        return self._port

    @property
    def location(self):
        # type:  () -> str
        return self._location

    @location.setter
    def location(self, value):
        # type:  (str) -> None
        self._location = value

    @staticmethod
    def find_sensors():
        # type: () -> List[str]
        _sensor_ports = []
        for port in serial.tools.list_ports.comports():
            if port.vid == int(USB_VID, 16) and port.pid == int(USB_PID, 16):
                _sensor_ports.append(port.device)
        return _sensor_ports

    def _read_data(self, command):
        # type: (str) -> Optional[str]

        if command not in self._available_read_cmds:
            raise ValueError('Invalid command requested: "{}"'.format(command))
        try:
            with LOCK:
                with serial.Serial(self._port, timeout=0.1, **SERIAL_SETTINGS) as ser:
                    # Dummy write to clean rubbish
                    ser.write("\r\n\r\n".encode("utf-8"))
                    result = ser.read(size=64).decode("utf-8")

                    ser.write("{}\r\n".format(command).encode("utf-8"))
                    result = ser.read(size=64).decode("utf-8")
                    if len(result) == 0:
                        result = None
                    else:
                        result = result.strip("\r\n")
                    return result
        except serial.SerialException as exc:

            error_message = "Cannot execute read command %s: %s" % (command, exc)
            logger.error(error_message)
            raise OSError(error_message)

    def _write_data(self, command, value):
        # type: (str, str) -> bool
        if command not in self._available_write_cmds:
            raise ValueError('Invalid command requested: "{}"'.format(command))
        try:
            with LOCK:
                with serial.Serial(self._port, timeout=0.1, **SERIAL_SETTINGS) as ser:
                    # Dummy write to clean rubbish
                    ser.write("\r\n\r\n".encode("utf-8"))
                    result = ser.read(size=64).decode("utf-8")

                    ser.write("{}={}\r\n".format(command, value).encode("utf-8"))
                    result = ser.read(size=64).decode("utf-8")
                    if result == "OK\n":
                        return True
                    logger.error(
                        "Command %s failed with result: %s" % (command, result)
                    )
                    return False
        except serial.SerialException as exc:
            message = "Cannot execute write command %s: %s" % (command, exc)
            logger.error(message)
            # Unless we use the led switch, we'll complain
            if command != "I":
                raise OSError(message)

    @property
    def model(self):
        # type:  () -> str
        return self._read_data("GI")

    @property
    def version(self):
        # type:  () -> str
        return self._read_data("GV")

    @property
    def temperature(self):
        # type:  () -> float
        data = self._read_data("GT")
        try:
            return float(data)
        except TypeError:
            return data

    @property
    def humidity(self):
        # type:  () -> float
        data = self._read_data("GH")
        try:
            return float(data)
        except TypeError:
            return data

    @property
    def pressure(self):
        # type:  () -> float
        data = self._read_data("GP")
        try:
            return float(data)
        except TypeError:
            return data

    @property
    def voc(self):
        # type:  () -> float
        data = self._read_data("GVOC")
        try:
            return float(data)
        except TypeError:
            return data

    @property
    def co2eq(self):
        # type:  () -> float
        data = self._read_data("GCO2")
        try:
            return float(data)
        except TypeError:
            return data

    @property
    def all(self):
        # type:  () -> dict
        data = json.loads(self._read_data("GJSON"))
        json_output = {}
        for element in data:
            if data[element]:
                try:
                    json_output[self._json_map_table[element]] = float(data[element])
                except TypeError:
                    json_output[self._json_map_table[element]] = data[element]
        return json_output

    @property
    def name(self):
        # type:  () -> str
        return self._read_data("GN")

    @name.setter
    def name(self, value):
        if isinstance(value, str) and 0 < len(value) <= 8:
            self._write_data("N", value)
        else:
            raise ValueError("Name cannot be longer than 8 characters")

    @property
    def led(self):
        # type: () -> bool
        return self._state_led

    @led.setter
    def led(self, value):
        # type:  (bool) -> None
        if isinstance(value, bool):
            self._write_data("I", "1" if value else "0")
            self._state_led = value
        else:
            raise ValueError(
                "led can only be turned on or off... Do not try to alter reality neo."
            )

    @property
    def identification(self):
        # type:  () -> dict
        return {"model": self.model, "version": self.version, "name": self.name}

    def __str__(self):
        return str(self.identification)
