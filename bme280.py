import adafruit_bme280

class Bme280:
    def __init__(self, i2c):
        self.__bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
    
    def get_temperature(self):
        return self.__bme280.temperature
    temperature = property(get_temperature)

    def get_humidity(self):
        return self.__bme280.relative_humidity
    humidity = property(get_humidity)

    def set_sea_level_pressure(self, hPa):
        self.__bme280.sea_level_pressure = hPa