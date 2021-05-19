from os import getenv
from iotdevice import IotDevice
from simulateddevice import SimulatedDevice
from raspberry_pi_device import RaspberryPi

class HybridDevice(IotDevice):
    def __init__(self):
        super().__init__()
        ip = getenv("IOTHUB_DEVICE_IP_ADDRESS", None)
        relay = getenv("IOTHUB_DEVICE_GPIO_RELAY", "SIM")
        if relay != "SIM":
            relay = int(relay)
        flow = getenv("IOTHUB_DEVICE_GPIO_FLOW", "SIM")
        if flow != "SIM":
            flow = int(flow)
        flowrate = getenv("IOTHUB_DEVICE_GPIO_FLOW_LPM", None)
        if flowrate != None:
            flowrate = float(flowrate)
        dht11 = getenv("IOTHUB_DEVICE_USE_DHT_11", "SIM")
        if dht11 != "SIM":
            dht11 = dht11 == "True"
        moisture = getenv("IOTHUB_DEVICE_MOISTURE", "SIM")
        if moisture != "SIM" and moisture != "I2C":
            raise ValueError("IOTHUB_DEVICE_MOISTURE must be SIM or I2C. Actual value is '{0}'".format(moisture))
        light = getenv("IOTHUB_DEVICE_LIGHT", "SIM")
        if light != "SIM":
            raise ValueError("IOTHUB_DEVICE_LIGHT must be SIM. Actual value is '{0}'".format(light))

        print ("ip: {0}".format(ip))
        print ("relay: {0}".format(relay))
        print ("flow: {0}".format(flow))
        print ("flowrate: {0}".format(flowrate))
        print ("dht11: {0}".format(dht11))
        print ("moisture: {0}".format(moisture))
        print ("light: {0}".format(light))

        pi = RaspberryPi(relay, flow, ip, dht11, moisture)
        sim = SimulatedDevice(flowrate)

        self.__device_valve = sim if relay=="SIM" else pi
        self.__device_dht = sim if dht11=="SIM" else pi
        self.__device_flow = sim if flow=="SIM" else pi
        self.__device_moist = sim if moisture=="SIM" else pi
        self.__device_light = sim if light=="SIM" else pi

    def get_valve(self):
        return self.__device_valve.get_valve()

    def turn_valve_on(self):
        self.__device_valve.turn_valve_on()

    def turn_valve_off(self):
        self.__device_valve.turn_valve_off()

    def get_humidity_and_temperature(self):
        return self.__device_dht.get_humidity_and_temperature()

    def get_flow(self):
        return self.__device_flow.get_flow()

    def get_moisture(self):
        return self.__device_moist.get_moisture()

    def get_light(self):
        return self.__device_light.get_light()