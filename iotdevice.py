from enum import Enum
from typing import ValuesView

class ValveState(Enum):
    open = 1
    closed = 2

class IotDevice:
    def __init__(self):
        self.turn_valve_off()
        self.__temperature = 0.0
        self.__humidity = 0.0
        self.__moisture = 0.0
        self.__light = 0.0
        self.__flow = 0.0

    def get_valve(self):
        return self.__valve

    valve = property(
        get_valve,
        doc="Set to ValveState.open to turn on water or ValveState.closed to turn off water.")

    def turn_valve_on(self):
        """
        This method should turn on the water.
        """
        self.__valve = ValveState.open

    def turn_valve_off(self):
        """
        This method should turn off the water.
        """
        self.__valve = ValveState.closed

    def get_flow(self):
        """
        This method should return the current flow rate (L/min).
        """
        return self.__flow

    def set_flow(self, value):
        self.__flow = value

    flow = property(
        get_flow,
        doc="The current rate of water flow in liters per minute.")

    def get_temperature(self):
        """
        This method should return the current temperature (F).
        """
        return self.__temperature

    def set_temperature(self, value):
        self.__temperature = value

    temperature = property(
        get_temperature,
        doc="The temperature in Fahrenheit.")

    def get_humidity(self):
        """
        This method should return the relative humidity (0 to 100).
        """
        return self.__humidity

    def set_humidity(self, value):
        self.__humidity = value

    humidity = property(
        get_humidity,
        doc="The relative humidity (0 to 100).")

    def get_moisture(self):
        """
        This method should return the moisture (0 to 10, 10=wet).
        """
        return self.__moisture

    def set_moisture(self, value):
        self.__moisture = value

    moisture = property(
        get_moisture,
        doc="The amount of moisture (where 0=dry to 10=wet).")

    def get_light(self):
        """
        This method should return the light (0 to 10, 10=sunny).
        """
        return self.__light

    def set_light(self, value):
        self.__light = value

    light = property(
        get_light,
        doc="The amount of light (where 0=dark to 10=sunny).")
