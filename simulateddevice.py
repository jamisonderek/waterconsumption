from iotdevice import IotDevice, ValveState
from datetime import datetime
import asyncio
import random
import requests

class SimulatedDevice(IotDevice):
    def __init__(self, flowrate=None, open_weather_api_key=None):
        super().__init__()
        super().set_light(2.4)
        super().set_humidity_and_temperature(30.0, 71.1)
        super().set_moisture(0.5)
        self.__flowrate = 6.2 if flowrate==None else flowrate
        self.__wet_offset = 0
        self.__open_weather_api_key = open_weather_api_key
        self.api_endpoint = None

        # spawn a task to update our data
        __update_task = asyncio.create_task(self.update_loop())
        # TODO: Cancel this task if our object gets deleted.

    def set_location(self, location):
        super().set_location(location)
        if self.__open_weather_api_key is not None:
            if self.location is not None and 'lat' in self.location and 'lon' in self.location:
                self.api_endpoint = ('http://api.openweathermap.org/data/2.5/weather?lat={0}&lon={1}&appid={2}&units=imperial'
                                     .format(self.location['lat'], self.location['lon'], self.__open_weather_api_key))

    def turn_valve_on(self):
        self.__wet_offset = 1.0 # After the valve is on, the ground is wetter.
        super().set_flow(self.__flowrate)
        super().turn_valve_on()

    def turn_valve_off(self):
        super().set_flow(0.0)
        super().turn_valve_off()

    def update_data(self):
        if self.api_endpoint is not None:
            try:
                r = requests.get(url=self.api_endpoint)
                # convert received data to json format.
                data = r.json()
                self._set_by_received_data(data)
            except Exception as e:
                print('encountered error while trying to get data from API: {0}.. switching to setting by generated data..'.format(e))
                self._set_by_generated_data()
        else:
            self._set_by_generated_data()
        
        # cannot get moisture through weather API. always set moisture by generated values.
        super().set_moisture(random.random()*1.5 + self.__wet_offset)

        # make ground wetter or dryer
        if self.__wet_offset > 0 and self.get_valve == ValveState.closed:
            self.__wet_offset = self.__wet_offset-0.05
        if self.__wet_offset < 9.5 and self.get_valve == ValveState.open:
            self.__wet_offset = self.__wet_offset+0.05
    
    def _set_by_generated_data(self):
        super().set_light(random.random()*10.0)
        super().set_humidity_and_temperature(humidity=random.random()*100.0, tempF=40.0+random.random()*40.0)

    def _set_by_received_data(self, data):
        # destruct json meaningfully.
        try:
            # TODO: These 2 variables return a brief description of the weather condition (cloudy, sunny, rainy).
            # Could we use this to determine if it is raining or not? If so could we use this to determine valve opening or closing??
            # weather = data['weather']['main']
            # weather_description = data['weather']['description']
            temperature_fahrenheit = data['main']['temp']
            humidity = data['main']['humidity']
            sunrise = data['sys']['sunrise']
            sunset = data['sys']['sunset']
            
            time_now = datetime.now().strftime('%H:%M:%S')
            sunrise_timestamp = datetime.fromtimestamp(sunrise).strftime('%H:%M:%S')
            sunset_timestamp = datetime.fromtimestamp(sunset).strftime('%H:%M:%S')

            # If time is within sunrise and sunset range then it is light.
            # If time is outside sunrise and sunset range then it is dark.
            # Scale 1-2 is easy.
            # How to determine on a scale of 1-10?

            if time_now<sunrise_timestamp or time_now>sunset_timestamp:
                super().set_light(random.random()*1.0)
            else:
                # TODO: Amount of light (set 1-10) based on time
                super().set_light(1.0 + random.random()*9.0)
            super().set_humidity_and_temperature(humidity=humidity, tempF=temperature_fahrenheit)
        except KeyError as e:
            print('JSON dictionary does not contain key {0}.. switching to setting by generated data..'.format(e))
            self._set_by_generated_data()

    async def update_loop(self):
        while True:
            self.update_data()
            await asyncio.sleep(10)