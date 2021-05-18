from enum import Enum
from typing import ValuesView

class ValveState(Enum):
    open = 1
    closed = 2

class IotDevice:
    def __init__(self):
        self.__timer = None
        self.turn_valve_off()
        self.__temperature = 0.0
        self.__humidity = 0.0
        self.__moisture = 0.0
        self.__light = 0.0
        self.__flow = 0.0

    def cancel_timer(self):
        if self.__timer != None:
            self.__timer.cancel()
            self.__timer = None

    def set_timer(self, timer):
        self.__timer = timer

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

    def get_humidity_and_temperature(self):
        """
        This method should return the relative humidity (0 to 100) and current temperature (F).
        """
        return (self.__humidity, self.__temperature)

    def set_humidity_and_temperature(self, humidity, tempF):
        self.__temperature = tempF
        self.__humidity = humidity

    humidity_and_temperature = property(
        get_humidity_and_temperature,
        doc="The relative humidity (0 to 100) and temperature in Fahrenheit.")

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

    def get_telemetry(self):
        humidity, tempF = self.get_humidity_and_temperature()
        telemetry = {
            'Valve': 'ValveState.open' if self.get_valve() == ValveState.open else 'ValveState.closed',
            'Flow': self.get_flow(),
            'Moisture': self.get_moisture(),
            'Light': self.get_light(),
            'Temperature': tempF,
            'Humidity': humidity
        }
        return telemetry