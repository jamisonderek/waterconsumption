from iotdevice import IotDevice
import asyncio
import random

class SimulatedDevice(IotDevice):
    def __init__(self):
        IotDevice.__init__(self)
        IotDevice.set_light(self, 2.4)
        IotDevice.set_humidity_and_temperature(self, 30.0, 71.1)
        IotDevice.set_moisture(self, 0.5)
        self.__wet_offset = 0
        # spawn a task to update our data
        __update_task = asyncio.create_task(self.update_loop())
        # TODO: Cancel this task if our object gets deleted.

    def turn_valve_on(self):
        self.__wet_offset = 3.0 # After the valve is on, the ground is wetter.
        IotDevice.set_flow(self, 6.2)
        IotDevice.turn_valve_on(self)

    def turn_valve_off(self):
        IotDevice.set_flow(self, 0.0)
        IotDevice.turn_valve_off(self)

    def update_data(self):
        IotDevice.set_light(self, random.random()*10.0)
        IotDevice.set_moisture(self, random.random()*1.5 + self.__wet_offset)
        IotDevice.set_humidity_and_temperature(self, 
            humidity=random.random()*100.0, tempF=40.0+random.random()*40.0)

    async def update_loop(self):
        while True:
            self.update_data()
            await asyncio.sleep(2)