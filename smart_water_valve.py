import os
import asyncio
import logging
import json

from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device.aio import ProvisioningDeviceClient
from azure.iot.device import Message, MethodResponse
from datetime import timedelta, datetime
from hybrid_device import HybridDevice
from iotdevice import IotDevice, ValveState
from threading import Timer

logging.basicConfig(level=logging.ERROR)

# The device "Thermostat" that is getting implemented using the above interfaces.
# This id can change according to the company the user is from
# and the name user wants to call this Plug and Play device
model_id = "dtmi:waterconsumption:SmartWaterValve;1"

#####################################################
# COMMAND HANDLERS : User will define these handlers
# depending on what commands the DTMI defines

async def turn_valve_on_handler(iot_device: IotDevice, values):
    iot_device.cancel_timer()
    if values and type(values) == int:
        duration = values
        print("Turning device on for {0} secs".format(duration))
        _auto_shutoff_timer(iot_device, duration)
    else:
        print("Turning device on.")
    iot_device.turn_valve_on()

async def turn_valve_off_handler(iot_device: IotDevice, values):
    iot_device.cancel_timer()
    print("Turning device off.")
    iot_device.turn_valve_off()

def _auto_shutoff_timer(iot_device: IotDevice, duration):
    timer = Timer(duration, _auto_shutoff_handlers, [iot_device])
    iot_device.set_timer(timer)
    timer.start()

def _auto_shutoff_handlers(iot_device: IotDevice):
    iot_device.cancel_timer()
    print("Auto shutoff, turning device off..")
    iot_device.turn_valve_off()

# END COMMAND HANDLERS
#####################################################

#####################################################
# CREATE RESPONSES TO COMMANDS

def serialize(response_dict):
    response_payload = json.dumps(response_dict, default=lambda o: o.__dict__, sort_keys=True)
    print(response_payload)
    return response_payload

async def turn_valve_on_response(iot_device: IotDevice, device_client, values):
    """
    :param values: The values that were received as part of the request.
    """
    response_dict = {"startTime": datetime.now().isoformat()}
    if values and type(values) == int:
        duration = values
        response_dict["endTime"] = (datetime.now() + timedelta(0, duration)).isoformat()
    return serialize(response_dict)

async def turn_valve_off_response(iot_device: IotDevice, device_client, values):
    response_dict = {
        "endTime": datetime.now().isoformat()
    }
    return serialize(response_dict)

# END CREATE RESPONSES TO COMMANDS
#####################################################

#####################################################
# TELEMETRY TASKS

async def send_telemetry_from_smart_valve(device_client, telemetry_msg):
    msg = Message(json.dumps(telemetry_msg))
    msg.content_encoding = "utf-8"
    msg.content_type = "application/json"
    print("Sending message {0}".format(msg))
    await device_client.send_message(msg)

# END TELEMETRY TASKS
#####################################################

#####################################################
# CREATE COMMAND AND PROPERTY LISTENERS

async def execute_command_listener(
    device_client, iot_device, method_name, user_command_handler, create_user_response_handler
):
    while True:
        if method_name:
            command_name = method_name
        else:
            command_name = None

        command_request = await device_client.receive_method_request(command_name)

        values = {}
        if command_request.payload:
            values = command_request.payload

        await user_command_handler(iot_device, values)

        response_status = 200
        response_payload = await create_user_response_handler(iot_device, device_client, values)

        command_response = MethodResponse.create_from_method_request(
            command_request, response_status, response_payload
        )

        try:
            await device_client.send_method_response(command_response)
        except Exception:
            print("responding to the {command} command failed".format(command=method_name))


# END COMMAND AND PROPERTY LISTENERS
#####################################################

#####################################################
# An KEYBOARD INPUT LISTENER to quit application

def stdin_listener():
    """
    Listener for quitting the sample
    """
    while True:
        selection = input("Press Q to quit\n")
        if selection == "Q" or selection == "q":
            print("Quitting...")
            break

# END KEYBOARD INPUT LISTENER
#####################################################


#####################################################
# PROVISION DEVICE
async def provision_device(provisioning_host, id_scope, registration_id, symmetric_key, model_id):
    provisioning_device_client = ProvisioningDeviceClient.create_from_symmetric_key(
        provisioning_host=provisioning_host,
        registration_id=registration_id,
        id_scope=id_scope,
        symmetric_key=symmetric_key,
    )
    provisioning_device_client.provisioning_payload = {"modelId": model_id}
    return await provisioning_device_client.register()


#####################################################
# MAIN STARTS
async def main():
    provisioning_host = "global.azure-devices-provisioning.net"
    id_scope = os.getenv("IOTHUB_DEVICE_DPS_ID_SCOPE")
    registration_id = os.getenv("IOTHUB_DEVICE_DPS_DEVICE_ID")
    symmetric_key = os.getenv("IOTHUB_DEVICE_DPS_DEVICE_KEY")

    # Check to see if they have dps id_scope, dps device_key, and dps device_id
    # filled out correctly..
    if (id_scope is None or id_scope == '<Your Scope Here...>' or 
        symmetric_key is None or symmetric_key == '<Your Key Here...>' or
        registration_id is None or registration_id == '<Your Device ID Here...>'):
        raise ValueError(
            'Make sure you have your device environment variables setup correctly! ' 
            'See https://github.com/jamisonderek/waterconsumption#obtaining-your-device-values')

    registration_result = await provision_device(
        provisioning_host, id_scope, registration_id, symmetric_key, model_id
    )

    if registration_result.status == "assigned":
        print("Device was assigned")
        print(registration_result.registration_state.assigned_hub)
        print(registration_result.registration_state.device_id)

        device_client = IoTHubDeviceClient.create_from_symmetric_key(
            symmetric_key=symmetric_key,
            hostname=registration_result.registration_state.assigned_hub,
            device_id=registration_result.registration_state.device_id,
            product_info=model_id,
        )
    else:
        raise RuntimeError(
            "Could not provision device. Aborting Plug and Play device connection."
        )

    # Connect the client.
    await device_client.connect()

    iot_device = HybridDevice()
    iot_device.turn_valve_off()

    ################################################
    # Set and read desired property (target temperature)

    #await device_client.patch_twin_reported_properties({"maxTempSinceLastReboot": max_temp})

    ################################################
    # Register callback and Handle command (reboot)
    print("Listening for command requests and property updates")

    listeners = asyncio.gather(
        execute_command_listener(
            device_client,
            iot_device,
            method_name="turnValveOn",
            user_command_handler=turn_valve_on_handler,
            create_user_response_handler=turn_valve_on_response,
        ),
        execute_command_listener(
            device_client,
            iot_device,
            method_name="turnValveOff",
            user_command_handler=turn_valve_off_handler,
            create_user_response_handler=turn_valve_off_response,
        )
    )

    ################################################
    # Send telemetry 

    async def send_telemetry():
        minute = datetime.now().minute

        while True:
            message = iot_device.get_telemetry()
            message.pop("Valve")
            await send_telemetry_from_smart_valve(device_client, message)

            # Delay, so we only send telemetry data once per minute.
            while datetime.now().minute == minute:
                await asyncio.sleep(2) # wait 2 seconds
            minute = datetime.now().minute            

    async def send_valve_telemetry():
        last_valve_data = None

        while True:
            valve = iot_device.get_valve()
            if valve != last_valve_data:
                last_valve_data = valve
                if (valve == ValveState.closed):
                    message = {"Valve": "ValveState.closed"}
                else:
                    message = {"Valve": "ValveState.open"}
                await send_telemetry_from_smart_valve(device_client, message)

            await asyncio.sleep(5) # Update the flow data every 5 seconds.

    async def twin_patch_handler(patch):
        print("the data in the desired properties patch was: {0}".format(patch))
        if "DeviceLocation" in patch:
            iot_device.set_location(patch["DeviceLocation"])
       
        ignore_keys = ["__t", "$version"]
        version = patch["$version"]
        prop_dict = {}

        for prop_name, prop_value in patch.items():
            if prop_name in ignore_keys:
                continue
            else:
                prop_dict[prop_name] = {
                    "ac": 200,
                    "ad": "Successfully executed patch",
                    "av": version,
                    "value": prop_value,
                }

        await device_client.patch_twin_reported_properties(prop_dict)

    device_client.on_twin_desired_properties_patch_received = twin_patch_handler

    twin = await device_client.get_twin()
    print("the twin was: {0}".format(twin))
    if "desired" in twin:
        twin = twin["desired"]
        if "DeviceLocation" in twin:
            iot_device.set_location(twin["DeviceLocation"])

    # Allow time for device to stablize before starting telemetry
    await asyncio.sleep(10) 
    send_telemetry_task = asyncio.create_task(send_telemetry())
    send_valve_telemetry_task = asyncio.create_task(send_valve_telemetry())

    # Run the stdin listener in the event loop
    loop = asyncio.get_running_loop()

    # Wait for user to indicate they are done listening for method calls
    user_finished = loop.run_in_executor(None, stdin_listener)
    await user_finished

    if not listeners.done():
        listeners.set_result("DONE")

    listeners.cancel()

    send_telemetry_task.cancel()
    send_valve_telemetry_task.cancel()

    # Finally, shut down the client
    await device_client.shutdown()


#####################################################
# EXECUTE MAIN

if __name__ == "__main__":
    asyncio.run(main())