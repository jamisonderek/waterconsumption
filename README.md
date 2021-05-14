# waterconsumption
This repository was made for the https://iotsustainabilityhack.devpost.com hackathon project.  The code runs on IoT devices (or a computer) and sends data to our Azure IoT Central subscription.

## Installing
This application has been tested using [Python 3.8.10](https://www.python.org/downloads/) but any newish version should work fine.<p/>
To install the application dependencies, please run the following command:
```
pip install -r requirements.txt
```

## Setup for debugging in Visual Studio Code
1. Go to your [Azure IoT Central portal](https://waterconsumption.azureiotcentral.com/admin/device-connection).
1. Click on **Administration**
1. Click on **Device connection**
1. In the Enrolement groups section, select **SAS-IoT-Devices**
1. Note down the *ID scope* (e.g. 0ne00xxxxxx)
1. Note down the Shared access signature *Primary Key*
1. Go to [portal.azure.com](https://portal.azure.com/#home)
1. Open the Cloud Shell (the icon is in the header of the site)
<svg width=32 height=32 viewBox="0 0 16 16" class="" role="presentation" focusable="false" xmlns:svg="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" id="FxSymbol0-005" data-type="333"><g><title></title><path d="M15 2v12H1V2h14m1-1H0v14h16V1z"></path><path d="M12.5 12h-4c-.3 0-.5-.2-.5-.5s.2-.5.5-.5h4c.3 0 .5.2.5.5s-.2.5-.5.5zM7.8 8.1s0-.1 0 0v-.5L3.7 4.3c-.2-.2-.5-.2-.7 0-.2.3-.1.6.1.7l3.5 3-3.5 3c-.2.2-.2.5-.1.7.1.1.2.2.4.2.1 0 .2 0 .3-.1l3.9-3.3v-.1c.2-.2.2-.2.2-.3 0 .1 0 0 0 0z"></path></g></svg>
1. Enter the command:
    ```
    az iot central device compute-device-key --device-id sample-device-01 --pk <<Your Primary Key from earlier step>>
    ```
    NOTE: Replace &lt;&lt;Your Primary Key&gt;&gt; with your actual key.<br/>
    NOTE: The 'sample-device-01' must match your IOTHUB_DEVICE_DPS_DEVICE_ID specified in the .vscode\launch.json file.
1. Update your .vscode\launch.json file IOTHUB_DEVICE_DPS_DEVICE_KEY with value obtained from running the previous step.
1. Update your .vscode\launch.json file IOTHUB_DEVICE_DPS_ID_SCOPE with value ID scope you noted down earlier.