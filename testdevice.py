from iotdevice import IotDevice
from simulateddevice import SimulatedDevice

import asyncio

async def main():
    device = IotDevice()
    #await testDevice(device)

    device = SimulatedDevice()
    await testDevice(device)

async def testDevice(device):
    print ("\n\nTesting {0} device.".format(type(device)))
    print ("Waiting 10 seconds to allow device to initialize.")
    await asyncio.sleep(10)

    print(device.get_telemetry())

    print ("Temperature is {0:.2f}F".format(device.temperature))
    print ("Humidity is {0:.2f} out of 100".format(device.humidity))
    print ("Light is {0:.2f} out of 10".format(device.light))
    print ("Moisture is {0:.2f} out of 10".format(device.moisture))
    print ("Flow is {0:.2f} Liters/minute".format(device.flow))
    print ("Valve is {0}".format(device.valve))

    print ("Turning on valve...")
    device.turn_valve_on()

    print ("Waiting 5 seconds for water to allow water to flow.")
    await asyncio.sleep(5)

    print ("Valve is {0}".format(device.valve))
    print ("Flow is {0} Liters/minute".format(device.flow))

    print ("Turning off valve...")
    device.turn_valve_off()

    print ("Waiting 5 seconds for water to allow water to stop.")
    await asyncio.sleep(5)

    print ("Valve is {0}".format(device.valve))
    print ("Flow is {0} Liters/minute".format(device.flow))

    print ("Temperature is {0:.2f}F".format(device.temperature))
    print ("Humidity is {0:.2f} out of 100".format(device.humidity))
    print ("Light is {0:.2f} out of 10".format(device.light))
    print ("Moisture is {0:.2f} out of 10".format(device.moisture))
    print ("Flow is {0:.2f} Liters/minute".format(device.flow))
    print ("Valve is {0}".format(device.valve))

if __name__ == "__main__":
    asyncio.run(main())
    