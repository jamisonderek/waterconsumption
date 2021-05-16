import Adafruit_DHT
import board
import busio

from gpiozero import LED
from gpiozero.pins.pigpio import PiGPIOFactory

from iotdevice import IotDevice

# TODO Brian: Add attributes for sensors. flow sensor,
# light sensor. Do we want to integrate some sort of weather tracker that
# scrapes for weather data?
class RaspberryPi(IotDevice):
    """ Class to interface with Raspberry Pi for
        an Automated Irrigation System. This Raspberry Pi
        setup actuates a solenoid valve that is collecting
        a variety of sensor data (Moisture, Flow,
        Humidity, Temperature).

    Attributes:
        gpio_relay: Integer. Indicates GPIO pin on Raspberry Pi
            for relay to actuate solenoid valve or an LED for testing.
        gpio_dht_22: Integer. Indicates GPIO pin on Raspberry Pi for dht22
            sensor (measures humidity and temperature).
        gpio_moisture: Integer. Indicates GPIO pin on Raspberry Pi for moisture
            sensor.
        gpio_flow: Integer. Indicates GPIO pin on Raspberry Pi for flow sensor.
        ip_address: Optional. A string. Indicates IP Address of Raspberry Pi.
            By default None. If provided, then use PiGPIOFactory library
            for remote GPIO control.
        dht_sensor: Optional. Adafruit_DHT object. By default the Adafruit DHT22
            to measure humidity and temperature. Indicates what DHT sensor type.
    """
    def __init__(self, gpio_relay, gpio_dht22,
                 gpio_flow, ip_address=None, dht_sensor=Adafruit_DHT.DHT22):
        IotDevice.__init__(self)

        if ip_address is not None:
            self.gpio_relay = LED(gpio_relay, PiGPIOFactory(host=ip_address))
        else:
            self.gpio_relay = LED(gpio_relay)

        self.dht_sensor = dht_sensor
        self.gpio_dht = gpio_dht22

        # For now we want to leave SCL to pin 3 and SDA to pin 2 for i2c interface.
        # meaning moisture sensor will need to be connected to these pins
        self.gpio_moisture = Seesaw(board.I2C(board.D3, board.D2), addr=0x36)
        self.gpio_flow = gpio_flow

    def get_humidity_and_temperature(self):
        """ Function to retrieve humidity and temperature data and then update model. """
        try:
            humidity, temperature = Adafruit_DHT.read_retry(
                self.dht_sensor, self.gpio_dht)

            if all((humidity, temperature)):
                # update model
                self.set_temperature(temperature)
                self.set_humidity(humidity)
        except Exception as e:
            print('Encountered error while trying to retrieve humidity and temeperature data: {0}'.format(e))

    def get_moisture(self):
        """ Function to retrieve moisture data and then update model """
        try:
            moist_val = self.gpio_moisture.moisture_read()
            self.set_moisture(moist_val)
        except Exception as e:
            print('Encountered error while trying to retrieve moisture data: {0}'.format(e))

    # Pulse -> Liters/min ???
    def get_flow(self):
        pass

    # turn_relay_on and turn_relay_off might be redundant
    # as it is just wrapping around gpiozero
    # and then updating state
    def turn_relay_on(self):
        """ Function to turn relay/LED on. """
        self.gpio_relay.on()
        # update model
        self.turn_valve_on()

    def turn_relay_off(self):
        """ Function to turn relay/LED off. """
        self.gpio_relay.off()
        # update model
        self.turn_valve_off()
