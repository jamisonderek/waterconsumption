from iotdevice import IotDevice
import asyncio
import random

class SimulatedDevice(IotDevice):
    def __init__(self):
        IotDevice.__init__(self)
        IotDevice.set_light(self, 2.4)
        IotDevice.set_humidity(self, 30.0)
        IotDevice.set_moisture(self, 4.0)
        IotDevice.set_temperature(self, 71.1)
        # spawn a task to update our data
        __update_task = asyncio.create_task(self.update_loop())
        # TODO: Cancel this task if our object gets deleted.

    def turn_valve_on(self):
        IotDevice.set_flow(self, 6.2)
        IotDevice.turn_valve_on(self)

    def turn_valve_off(self):
        IotDevice.set_flow(self, 0.0)
        IotDevice.turn_valve_off(self)

    def update_data(self):
        IotDevice.set_light(self, random.random()*10.0)
        IotDevice.set_moisture(self, random.random()*10.0)
        IotDevice.set_humidity(self, random.random()*100.0)
        IotDevice.set_temperature(self, 40.0+random.random()*40.0)

    async def update_loop(self):
        while True:
            self.update_data()
            await asyncio.sleep(2)