import adafruit_dht
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

    Args:
        gpio_relay: Integer. Indicates GPIO pin on Raspberry Pi
            for relay to actuate solenoid valve or an LED for testing.
        gpio_flow: Integer. Indicates GPIO pin on Raspberry Pi for flow sensor.
        ip_address: Optional. A string. Indicates IP Address of Raspberry Pi.
            By default None. If provided, then use PiGPIOFactory package
            for remote GPIO control.

    Attributes:
        dht_sensor: DHT22 sensor to measure humidity and temperature. connected
            to pin 18 for now.
        moisture_sensor: connected to pin 3 and pin 2 for now
    """
    def __init__(self, gpio_relay, gpio_flow, ip_address=None):
        IotDevice.__init__(self)

        if ip_address is not None:
            self.gpio_relay = LED(gpio_relay, PiGPIOFactory(host=ip_address))
        else:
            print('in here')
            self.gpio_relay = LED(gpio_relay)

        # For now we want to leave the DHT_22 sensor (measures temperature and humidity)
        # connected to pin 18.
        self.dht_sensor = adafruit_dht.DH22(board.D18)

        # For now we want to leave SCL to pin 3 and SDA to pin 2 for i2c interface.
        # meaning moisture sensor will need to be connected to these pins
        self.moisture_sensor = Seesaw(board.I2C(board.D3, board.D2), addr=0x36)
        self.gpio_flow = gpio_flow

    def get_humidity_and_temperature(self):
        """ Function to retrieve humidity and temperature data and then update model. """
        temperature_f, humidity = None, None

        while humidity is None and temperature_f is None:
            try:
                temperature_c = self.dht_sensor.temperature
                temperature_f = temperature_c * (9 / 5) + 32
                humidity = self.dht_sensor.humidity
            except RuntimeError as err:
                # DHT's are hard to read, keep going
                time.sleep(2.0)
                continue
            except Exception as err:
                print('Encountered error while trying to retrieve humidity and temeperature data: {0}'.format(e))

        # update model
        self.set_temperature(temperature_f)
        self.set_humidity(humidity)

    def get_moisture(self):
        """ Function to retrieve moisture data and then update model """
        try:
            moist_val = self.moisture_sensor.moisture_read()
            # upate model
            self.set_moisture(moist_val)
        except Exception as e:
            print('Encountered error while trying to retrieve moisture data: {0}'.format(e))

    # Pulse -> Liters/min ??
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
