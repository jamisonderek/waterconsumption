from bme280 import Bme280
import busio

try:
    import adafruit_dht
except ImportError:
    print ("\033[91mError importing DHT code -- Are you running on an IoT device?\033[0m")

try:
    import board
except NotImplementedError:
    print ("\033[91mError importing board -- Are you running on an IoT device?\033[0m")

from adafruit_seesaw.seesaw import Seesaw
from gpiozero import LED
from gpiozero.pins.pigpio import PiGPIOFactory
from gpio_frequency import FrequencySignal
from iotdevice import IotDevice
from time import sleep

# TODO Brian: Add attributes for light sensor. 
# TODO: Do we want to integrate some sort of weather tracker that
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
        use_dht_11: Optional. A boolean. When set to True a DHT11 will be used
            instead of the DHT22.  By default False.
        moisture: Optional. A String. "I2C" or "SIM" (for simulated device).
            By default "I2C".

    Attributes:
        dht_sensor: DHT22 sensor to measure humidity and temperature. connected
            to pin 18 for now.
        moisture_sensor: connected to pin 3 and pin 2 for now
    """
    def __init__(self, gpio_relay, gpio_flow, ip_address=None, humid_temp="DHT22", moisture="I2C"):
        IotDevice.__init__(self)

        if gpio_relay == "SIM":
            self.gpio_relay = None
        else:
            if ip_address is not None:
                self.gpio_relay = LED(gpio_relay, PiGPIOFactory(host=ip_address))
            else:
                self.gpio_relay = LED(gpio_relay)

        # For now we want to leave the DHT sensor (measures temperature and humidity)
        # connected to pin 18.
        if humid_temp == "BME280":
            i2c = board.I2C()
            self.ht_sensor = Bme280(i2c)
            self.ht_sensor.set_sea_level_pressure(1022.2)
        elif humid_temp == "DHT11":
            self.ht_sensor = adafruit_dht.DHT11(board.D18)
        elif humid_temp == "DHT22":
            self.ht_sensor = adafruit_dht.DHT22(board.D18)
        else:
            self.ht_sensor = None

        # For now we want to leave SCL to pin 3 and SDA to pin 2 for i2c interface.
        # meaning moisture sensor will need to be connected to these pins
        if moisture == "SIM":
            self.moisture_sensor = None
        else:
            self.moisture_sensor = Seesaw(busio.I2C(board.D3, board.D2), addr=0x36)

        if gpio_flow == "SIM":
            self.gpio_flow = None
        else:
            self.gpio_flow = FrequencySignal(gpio_flow)

    def get_humidity_and_temperature(self):
        """ Function to retrieve humidity and temperature data and then update model. """
        temperature_f, humidity = None, None

        while humidity is None and temperature_f is None:
            try:
                temperature_c = self.ht_sensor.temperature
                temperature_f = temperature_c * (9 / 5) + 32
                humidity = self.ht_sensor.humidity
            except RuntimeError as err:
                # DHT's are hard to read, keep going
                sleep(2.0)
                continue
            except Exception as e:
                print('Encountered error while trying to retrieve humidity and temeperature data: {0}'.format(e))
                return (None, None)

        # update model
        self.set_humidity_and_temperature(humidity, temperature_f)
        return super().get_humidity_and_temperature()

    def get_moisture(self):
        """ Function to retrieve moisture data and then update model """
        try:
            moist_val = self.moisture_sensor.moisture_read()
            moist_val -= 300
            moist_val *= 0.014
            if moist_val < 0:
                moist_val = 0
            if moist_val > 10:
                moist_val = 10
            # upate model
            self.set_moisture(moist_val)
        except Exception as e:
            print('Encountered error while trying to retrieve moisture data: {0}'.format(e))
        return super().get_moisture()

    def get_flow(self):
        """ Funtion to retrieve flow data and then update model """

        try:
            # For our device you get 3.1Hz for each Liter/minute of water
            rate = 3.1  # Adjust this based on testing your device.
            self.set_flow(self.gpio_flow.measure_frequency() / rate)
        except Exception as e:
            print('Encountered error while trying to retrieve flow data: {0}'.format(e))
        return super().get_flow()

    def turn_valve_on(self):
        """ Function to turn relay/LED on. """

        try:
            self.gpio_relay.on()
        except Exception as e:
            print('Encountered error while trying to turn relay on: {0}'.format(e))
        # update model
        super().turn_valve_on()

    def turn_valve_off(self):
        """ Function to turn relay/LED off. """

        try:
            self.gpio_relay.off()
        except Exception as e:
            print('Encountered error while trying to turn relay off: {0}'.format(e))
        # update model
        super().turn_valve_off()
