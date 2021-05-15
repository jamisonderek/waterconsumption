from iotdevice import IotDevice

from gpiozero import LED
from gpiozero.pins.pigpio import PiGPIOFactory

import gpiozero

import RPi.GPIO as GPIO
import Adafruit_DHT
import time

from time import sleep

# TODO Brian: Add attributes for sensors. moisture, flow sensor,
# light sensor. Do we want to integrate some sort of weather tracker that
# scrapes for weather data?
# actually the gpiozero library is essentially a wrapper around rpi.GPIO. need
# to stick to one
class RaspberryPi(IotDevice):
    """ Class to interface with Raspberry Pi for
        an Automated Irrigation System. This Raspberry Pi
        setup actuates a solenoid valve that is collecting
        a variety of sensor data Moisture, Flow,
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
            By default None. If provided, then use gpiozero third party library
            to control GPIO remotely.
        dht_sensor: Optional. Adafruit_DHT object. By default the Adafruit DHT22
            to measure humidity and temperature. Indicates what DHT sensor type.
    """
    def __init__(self, gpio_relay, gpio_dht22, gpio_moisture,
                 gpio_flow, ip_address=None, dht_sensor=Adafruit_DHT.DHT22):
        IotDevice.__init__(self)

        self.gpio_relay = gpio_relay
        self.gpio_dht = gpio_dht22
        self.gpio_moisture = gpio_moisture
        self.gpio_flow = gpio_flow

        self.dht_sensor = dht_sensor
        self.ip_address = ip_address

        self._setup_pi_gpio()

    #TODO: Integrate gpiozero third party library to control GPIO remotely
    def _setup_pi_gpio(self):
        """ Helper function to setup the output GPIO pins. """
        if self.ip_address:
            pass
        else:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)

            GPIO.setup(self.gpio_relay, GPIO.OUT)

    def get_humidity_and_temperature(self):
        """ Function to return humidity and temperature data.

        Returns:
            A tuple. First element is humidity (float) and
                second element is temperature (float).
        """
        try:
            humidity, temperature = Adafruit_DHT.read_retry(
                self.dht_sensor, self.gpio_dht)

            if all((humidity, temperature)):
                # update model
                self.set_temperature(temperature)
                self.set_humidity(humidity)
        except Exception as e:
            print('Encountered error while trying to retrieve data: {0}'.format(e))

    # TODO: Implement moisture & flow
    def get_moisture(self):
        pass

    # Liters/min
    def get_flow(self):
        pass

    def turn_relay_on(self, use_led=False):
        """ Function to turn relay/LED on.

        Args:
            use_led: Boolean. By default False. Set to True if using a LED
        """
        on = GPIO.HIGH if use_led else GPIO.LOW
        GPIO.output(self.gpio_relay, on)
        # update model
        self.turn_valve_on()

    def turn_relay_off(self, use_led=False):
        """ Function to turn relay/LED on.

        Args:
            use_led: Boolean. By default False. Set to True if using a LED
        """
        off = GPIO.LOW if use_led else GPIO.HIGH
        GPIO.output(self.gpio_relay, off)
        # update model
        self.turn_valve_off()





# factory = PiGPIOFactory(host='192.168.1.6')
#
# red = LED(17,pin_factory=factory)
#
# while True:
#
# red.on()
#
# sleep(1)
#
# red.off()
#
# sleep(1)
