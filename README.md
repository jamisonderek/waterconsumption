# waterconsumption
This repository was made for the https://iotsustainabilityhack.devpost.com hackathon project.  The code runs on IoT devices (or a computer) and sends data to our Azure IoT Central subscription.

## Installing
This application has been tested using [Python 3.8.10](https://www.python.org/downloads/) but any newish version should work fine.<p>
To install the application dependencies, please run the following command:
```
pip3 install -r requirements.txt
```

## Obtaining your device values
The following steps will help you obtain your IOTHUB_DEVICE_DPS_ID_SCOPE, IOTHUB_DEVICE_DPS_DEVICE_ID and IOTHUB_DEVICE_DPS_DEVICE_KEY values.
1. Go to your [Azure IoT Central portal](https://waterconsumption.azureiotcentral.com/admin/device-connection).
1. Click on **Administration**
1. Click on **Device connection**
1. In the Enrolement groups section, select **SAS-IoT-Devices**
1. Note down the *ID scope* (e.g. 0ne00xxxxxx).  This is your **IOTHUB_DEVICE_DPS_ID_SCOPE**
1. Note down the Shared access signature *Primary Key*
1. Go to [portal.azure.com](https://portal.azure.com/#home)
1. Open the Cloud Shell (the icon is in the header of the site)
<svg width=32 height=32 viewBox="0 0 16 16" class="" role="presentation" focusable="false" xmlns:svg="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" id="FxSymbol0-005" data-type="333"><g><title></title><path d="M15 2v12H1V2h14m1-1H0v14h16V1z"></path><path d="M12.5 12h-4c-.3 0-.5-.2-.5-.5s.2-.5.5-.5h4c.3 0 .5.2.5.5s-.2.5-.5.5zM7.8 8.1s0-.1 0 0v-.5L3.7 4.3c-.2-.2-.5-.2-.7 0-.2.3-.1.6.1.7l3.5 3-3.5 3c-.2.2-.2.5-.1.7.1.1.2.2.4.2.1 0 .2 0 .3-.1l3.9-3.3v-.1c.2-.2.2-.2.2-.3 0 .1 0 0 0 0z"></path></g></svg>
1. Decide on a unique device id for your device, for example "sample-device-01".  This is your **IOTHUB_DEVICE_DPS_DEVICE_ID**
1. Enter the command:
    ```
    az iot central device compute-device-key --device-id sample-device-01 --pk <<Your Primary Key from earlier step>>
    ```
    NOTE: Replace &lt;&lt;Your Primary Key&gt;&gt; with your actual key.<br/>
    NOTE: Replace sample-device-01 with your *IOTHUB_DEVICE_DPS_DEVICE_ID*.
1. Note down the output of the command.  This is your **IOTHUB_DEVICE_DPS_DEVICE_KEY**

## Environment variables
On Windows, you can set an environment variable using the command:
```
set VARIABLENAME=VALUE
```

On Linux, you can set an environment variable using the command:
```
EXPORT VARIABLENAME VALUE
```

In Visual Studio Code, you can set an envionment variable using the .vscode/launch.json file.  


Variable | Supported Values | Recommended value | Comment
------|------|-------|-----
IOTHUB_DEVICE_GPIO_RELAY | "SIM" or pin | 16 | The GPIO pin connected to the relay to turn the water on/off.
IOTHUB_DEVICE_GPIO_FLOW | "SIM" or pin | 13 | The GPIO pin connected to the flow meter.
IOTHUB_DEVICE_GPIO_FLOW_LPM | double | 25.0 | The flow rate (liters/minute) when the relay is on (used when GPIO_FLOW is set to SIM).
IOTHUB_DEVICE_HUMIDITY_TEMP | "SIM", "DHT11", "DHT22", "BME280" | "DHT22" | If "DHT11" or "DHT22" connect to GPIO18 (pin 12).  If "BME280" connect to SDA/SCL of I2C (pins 3 & 5).
IOTHUB_DEVICE_MOISTURE | "SIM" or "I2C" | "I2C" | If "I2C" connect moisture sensor to SDA/SCL of I2C (pins 3 & 5).
IOTHUB_DEVICE_LIGHT | "SIM" | "SIM" | Light sensor (Adafruit VEML7700) is not supported yet, so use "SIM".
IOTHUB_DEVICE_DPS_DEVICE_ID | device id | "smart-water-valve-01" | This should be a unique ID to identify your device.  See [Obtaining your device values](#obtaining-your-device-values) section.
IOTHUB_DEVICE_DPS_ID_SCOPE | scope | "0ne...F2" | See [Obtaining your device values](#obtaining-your-device-values) section.
IOTHUB_DEVICE_DPS_DEVICE_KEY | key | "r+itP...kIa0=" | See [Obtaining your device values](#obtaining-your-device-values) section.

## Configuring I2C on your Raspberry Pi

Make sure your I2C interface is enabled:
```
sudo raspi-config
(choose "Interface options")
(then enable the "I2C" interface)
```
You may need to reboot your device after making changes.

```
sudo i2cdetect -y 1
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- 36 -- -- -- -- -- -- -- -- --
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
70: -- -- -- -- -- -- 76 --
```
1. If you have an Adafruit moisture sensor, it should be on address 0x36.
1. If you have an Adafruit BME280 sensor, it should be on address 0x76.  (If it is on address 0x77 then update the code in bme280.py, replacing 0x76 with 0x77.  The other option is there is usually something on your hardware, jumper/trace/etc. that can be modified to change the address.)
1. If all entries in the table show -- and you have hardware connected, double check your SDA/SCL wires are not swapped and that your 3.3V and GND wires have a good connection to both the Pi and the sensor.

## Debugging in Visual Studio Code
1. Make sure you updated the .vscode\launch.json file with all of the proper [environment values](#environment-variables)
1. Open and select the "smart_water_valve.py" file.
1. Choose *Start Debugging* from the *Run* menu.

