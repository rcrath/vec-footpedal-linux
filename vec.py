
import uinput
from typing import Union
import evdev
import argparse
import time
import sys
import os

# Create virtual mouse device
virtual_mouse = uinput.Device([
    uinput.BTN_LEFT,
    uinput.BTN_RIGHT,
    uinput.BTN_MIDDLE,
    uinput.REL_X,
    uinput.REL_Y,
])

############## Define your actions here ##############
def middle_press():
    virtual_mouse.emit(uinput.BTN_MIDDLE, 1)

def middle_release():
    virtual_mouse.emit(uinput.BTN_MIDDLE, 0)

def left_press():
    virtual_mouse.emit(uinput.BTN_LEFT, 1)

def left_release():
    virtual_mouse.emit(uinput.BTN_LEFT, 0)

def right_press():
    virtual_mouse.emit(uinput.BTN_RIGHT, 1)

def right_release():
    virtual_mouse.emit(uinput.BTN_RIGHT, 0)

button_actions = {
    'LEFT_PRESS': (lambda: middle_press()),
    'LEFT_RELEASE': (lambda: middle_release()),

    'MIDDLE_PRESS': (lambda: left_press()),
    'MIDDLE_RELEASE': (lambda: left_release()),

    'RIGHT_PRESS': (lambda: right_press()),
    'RIGHT_RELEASE': (lambda: right_release()),
}
#####################################################

VENDOR_ID = 0x05f3
PRODUCT_ID = 0x00ff
VERSION_ID = 0x0100

DEBUG_MODE = False
RETRY_DELAY_SECONDS = 5

def find_device_path(vendor_id: int, product_id: int, version_id: int) -> Union[str, None]:
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    for device in devices:
        dev_info = device.info

        if (dev_info.vendor == vendor_id and dev_info.product == product_id and dev_info.version == version_id):
            return device.path

    return None

def get_event_path_for_correct_device() -> str:
    while (event_dev_path := find_device_path(VENDOR_ID, PRODUCT_ID, VERSION_ID)) is None:
        print(f"No device found or permission denied. Trying again in {RETRY_DELAY_SECONDS} seconds...")
        time.sleep(RETRY_DELAY_SECONDS)

    return event_dev_path

# Trigger Event Codes: LEFT=256, MIDDLE=257, RIGHT=258
trigger_event_codes = {
    256: 'LEFT',
    257: 'MIDDLE',
    258: 'RIGHT',
}
# Trigger Event Values: 1=press, 0=release
trigger_event_values = {
    1: 'PRESS',
    0: 'RELEASE',
}

def parse_args():
    parser = argparse.ArgumentParser(description="Foot Pedal Mapper Script")
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    return parser.parse_args()

def main():
    global DEBUG_MODE

    args = parse_args()
    DEBUG_MODE = args.debug

    event_path = get_event_path_for_correct_device()
    print(f"Using event path: '{event_path}'")

    device = evdev.InputDevice(event_path)
    for event in device.read_loop():
        try:
            if event.type == evdev.ecodes.EV_KEY:
                trigger_event_code = event.code
                trigger_event_value = event.value

                event_name = trigger_event_codes.get(trigger_event_code)
                event_event = trigger_event_values.get(trigger_event_value)

                if event_name and event_event:
                    event_action = f"{event_name}_{event_event}"
                    action_fn = button_actions.get(event_action)

                    if action_fn is not None:
                        action_fn()

                    if DEBUG_MODE:
                        print(f"Event: event.type={event.type}, event.code={event.code}, event.value={event.value}, event_name={event_name}, event_event={event_event}, event_action={event_action}")
        except Exception as e:
            print(f"Error in loop: {e}")

if __name__ == '__main__':
    while True:
        print("Starting...")
        try:
            main()
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}. Restarting...")
