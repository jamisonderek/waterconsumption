from iotdevice import IotDevice, ValveState
import asyncio
import random

class SimulatedDevice(IotDevice):
    def __init__(self, flowrate=None):
        super().__init__()
        super().set_light(2.4)
        super().set_humidity_and_temperature(30.0, 71.1)
        super().set_moisture(0.5)
        self.__flowrate = 6.2 if flowrate==None else flowrate
        self.__wet_offset = 0
        # spawn a task to update our data
        __update_task = asyncio.create_task(self.update_loop())
        # TODO: Cancel this task if our object gets deleted.

    def turn_valve_on(self):
        self.__wet_offset = 1.0 # After the valve is on, the ground is wetter.
        super().set_flow(self.__flowrate)
        super().turn_valve_on()

    def turn_valve_off(self):
        super().set_flow(0.0)
        super().turn_valve_off()

    def update_data(self):
        super().set_light(random.random()*10.0)
        super().set_moisture(random.random()*1.5 + self.__wet_offset)
        super().set_humidity_and_temperature(humidity=random.random()*100.0, tempF=40.0+random.random()*40.0)
        # make ground wetter or dryer
        if self.__wet_offset > 0 and self.get_valve == ValveState.closed:
            self.__wet_offset = self.__wet_offset-0.01
        if self.__wet_offset < 3 and self.get_valve == ValveState.open:
            self.__wet_offset = self.__wet_offset+0.01

    async def update_loop(self):
        while True:
            self.update_data()
            await asyncio.sleep(2)