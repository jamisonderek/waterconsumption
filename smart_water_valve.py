from iotdevice import IotDevice
import os
import asyncio
import logging
import json

from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device.aio import ProvisioningDeviceClient
from azure.iot.device import constant, Message, MethodResponse
from datetime import date, timedelta, datetime

from simulateddevice import SimulatedDevice

logging.basicConfig(level=logging.ERROR)

# The device "Thermostat" that is getting implemented using the above interfaces.
# This id can change according to the company the user is from
# and the name user wants to call this Plug and Play device
model_id = "dtmi:waterconsumption:SmartWaterValve;1"

#####################################################
# COMMAND HANDLERS : User will define these handlers
# depending on what commands the DTMI defines

async def turn_valve_on_handler(iot_device: IotDevice, values):
    # TODO: Cancel any previous timer.
    if values and type(values) == int:
        print("Turning device on for {count} secs".format(count=values))
        # TODO: Set a timer to turn off device.
    else:
        print("Turning device on.")
    iot_device.turn_valve_on()

async def turn_valve_off_handler(iot_device: IotDevice, values):
    # TODO: Cancel any timers from turn_valve_on_handler
    print("Turning device off.")
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
    await send_telemetry_from_smart_valve(device_client,{"Valve": "ValveState.open"})
    return serialize(response_dict)

async def turn_valve_off_response(iot_device: IotDevice, device_client, values):
    response_dict = {
        "endTime": datetime.now().isoformat()
    }
    await send_telemetry_from_smart_valve(device_client,{"Valve": "ValveState.closed"})
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


async def execute_property_listener(device_client):
    ignore_keys = ["__t", "$version"]
    while True:
        patch = await device_client.receive_twin_desired_properties_patch()  # blocking call

        print("the data in the desired properties patch was: {}".format(patch))

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

    # TODO: Replace with real device.
    iot_device = SimulatedDevice()

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
        ),
        execute_property_listener(device_client),
    )

    ################################################
    # Send telemetry 

    async def send_telemetry():
        print("Sending telemetry for smart valve")
        sent_valve_data = False

        while True:
            await asyncio.sleep(15)
            message = iot_device.get_telemetry()
            if sent_valve_data:
                message.pop("Valve")  # Remove the Valve data, since we already sent that information.
            else:
                sent_valve_data = True
            await send_telemetry_from_smart_valve(device_client, message)

    send_telemetry_task = asyncio.create_task(send_telemetry())

    # Run the stdin listener in the event loop
    loop = asyncio.get_running_loop()

    # Wait for user to indicate they are done listening for method calls
    user_finished = loop.run_in_executor(None, stdin_listener)
    await user_finished

    if not listeners.done():
        listeners.set_result("DONE")

    listeners.cancel()

    send_telemetry_task.cancel()

    # Finally, shut down the client
    await device_client.shutdown()


#####################################################
# EXECUTE MAIN

if __name__ == "__main__":
    asyncio.run(main())