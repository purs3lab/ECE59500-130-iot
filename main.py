from common import *
from lcd import LCD
import sys
import time
import os
import json
import asyncio
import ecdsa_verify
from machine import I2C, Pin

# How long a device's response to a challenge stays valid before it's
# rejected as stale - see README.md#controller-via-cloud, "Pending-nonce TTL".
UNLOCK_NONCE_TTL_MS = 15_000

# Guards do_unlock() so a keypad unlock and a cloud unlock can't both be
# mid-flight at once (racing LCD writes / relock timers).
unlock_lock = asyncio.Lock()

# Single pending session for whichever of pairing/unlock is in flight -
# same "one active session at a time" pattern part2 used for BLE pairing.
_pending_pair_session = None
_pending_unlock_nonce = None

def verify_signature(pub_key, message, signature):
    try:
        return ecdsa_verify.verify(pub_key, message, signature)
    except Exception as e:
        print("Signature verification failed:", e)
        return False

def _publish(topic, payload):
    if mqtt is None:
        return
    try:
        mqtt.publish(topic, json.dumps(payload))
    except Exception as e:
        print("Failed to publish to", topic, ":", e)

async def do_unlock(action, reason=None):
    pass

async def send_attestation():
    pass

def _start_pairing_session():
    pass

def _handle_pairing_request(data):
    pass

async def pair_device_cloud():
    pass

async def list_paired_devices():
    pass

async def remove_device():
    pass

def _handle_command(data):
    pass

def _handle_unlock_response(data):
    pass

def _handle_command_message(topic, msg):
    pass

async def command_main():
    pass


def display_admin_panel():
    lcd.message("1. Cloud Pair\n2. Remove device")

async def admin_panel():
    pass

async def keypad_main():
    pass

async def main():
    global lcd, mqtt

    i2c = I2C(0, sda=Pin(16), scl=Pin(17), freq=400000)
    lcd = LCD(i2c)
    lcd.message("System Startup.")
    
    # TODO: connect_wifi() / get_mqtt_client() (same pattern as init.py),
    # tolerating failure - the lock must keep working without wifi. Send a
    # BOOT log message, then send_attestation() once per boot.
    #
    # If the MQTT client came up, start command_main() as a background
    # task (asyncio.create_task) so cloud pairing/unlock work even before
    # anyone touches the keypad.
    #

    await keypad_main()

asyncio.run(main())
