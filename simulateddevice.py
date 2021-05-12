from iotdevice import IotDevice

class SimulatedDevice(IotDevice):
    def __init__(self):
        IotDevice.__init__(self)
        IotDevice.set_light(self, 2.4)
        IotDevice.set_humidity(self, 30.0)
        IotDevice.set_moisture(self, 4.0)
        IotDevice.set_temperature(self, 71.1)

    def turn_valve_on(self):
        IotDevice.set_flow(self, 6.2)
        IotDevice.turn_valve_on(self)

    def turn_valve_off(self):
        IotDevice.set_flow(self, 0.0)
        IotDevice.turn_valve_off(self)
