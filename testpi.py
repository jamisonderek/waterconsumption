import asyncio

from iotdevice import IotDevice
from raspberry_pi_device import RaspberryPi

async def main():
    device = RaspberryPi(gpio_relay=9, gpio_flow=10)
    await testDevice(device)
        
def printTelemetry(device: IotDevice):
    print(device.get_telemetry())
    humidity, tempF = device.humidity_and_temperature
    print ("Temperature is {0:.2f}F".format(tempF))
    print ("Humidity is {0:.2f} out of 100".format(humidity))
    print ("Light is {0:.2f} out of 10".format(device.light))
    print ("Moisture is {0:.2f} out of 10".format(device.moisture))
    print ("Flow is {0:.2f} Liters/minute".format(device.flow))
    print ("Valve is {0}".format(device.valve))

async def testDevice(device: IotDevice):
    print ("\n\nTesting {0} device.".format(type(device)))
    printTelemetry(device)

    print ("\nTurning on valve, then waiting 5 seconds...")
    device.turn_valve_on()
    await asyncio.sleep(5)

    printTelemetry(device)
    if device.get_flow() == 0:
        print ("\033[93mWARNING: *** NO FLOW DETECTED ***\033[0m")

    print ("\nTurning off valve, then waiting 5 seconds...")
    device.turn_valve_off()
    await asyncio.sleep(5)

    printTelemetry(device)
    if device.get_flow() != 0:
        print ("\033[93mWARNING: *** FLOW DETECTED ***\033[0m")

if __name__ == "__main__":
    asyncio.run(main())
    