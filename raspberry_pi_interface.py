from gpiozero import LED
from gpiozero.pins.pigpio import PiGPIOFactory

import RPi.GPIO as GPIO
import time

# TODO Brian: Add attributes for sensors. humidity, moisture, flow sensor, temperature,
# light sensor
class RaspberryPi():
    """ Class to interface with Raspberry Pi for
        an Automated Irrigation System. This Raspberry Pi
        setup actuates a solenoid valve that is collecting
        various amounts of sensor data.

    Attributes:
        gpio_relay: Integer. Indicates GPIO pin on Raspberry Pi
            for relay to actuate solenoid valve.
        ip_address: Optional. A string. Indicates IP Address of Raspberry Pi.
            By default None. If provided, then use gpiozero third party library
            to control GPIO remotely.
    """
    def __init__(self, gpio_relay, ip_address=None):
        self.gpio_relay = gpio_relay
        self.ip_address = self.ip_address

        self._setup_pi_gpio()


    def _setup_pi_gpio(self):
        if self.ip_adress:
            pass
        else:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(self.gpio_relay, GPIO.OUT)
