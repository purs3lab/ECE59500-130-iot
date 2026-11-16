from common import *
from lcd import LCD
import sys
import time
import os
import json
import asyncio
import binascii
import machine
import ecdsa_verify
from machine import I2C, Pin

# How long a device's response to a challenge stays valid before it's
# rejected as stale - see part3's README.md#controller-via-cloud,
# "Pending-nonce TTL".
UNLOCK_NONCE_TTL_MS = 15_000
# See README.md#remote-updates.
MAX_UPDATE_SIZE = 200_000
UPDATE_TMP_SUFFIX = ".update.tmp"
ROLLBACK_FLAG_FILE = "pending_rollback_report.flag"

# 8000ms is close to the RP2350 hardware ceiling (~8388ms - the watchdog
# counter is 24-bit at 1MHz). Fed at a fraction of this from a dedicated
# task below, so there's margin even if that task's turn is briefly
# delayed by other work.
WDT_TIMEOUT_MS = 8000
# Create: open("enable_wdt.flag", "w").close()
# Delete: os.remove("enable_wdt.flag")
WDT_ENABLE_FLAG = "enable_wdt.flag"

# Guards do_unlock() so a keypad unlock and a cloud unlock can't both be
# mid-flight at once (racing LCD writes / relock timers).
unlock_lock = asyncio.Lock()

# Single pending session for whichever of pairing/unlock is in flight -
# same "one active session at a time" pattern part2 used for BLE pairing.
_pending_pair_session = None
_pending_unlock_nonce = None

# Set from main() if the watchdog is armed (see WDT_ENABLE_FLAG), else
# stays None - verify_signature()'s feed_cb param is a no-op in that case.
wdt = None

def verify_signature(pub_key, message, signature, feed_cb=None):
    try:
        return ecdsa_verify.verify(pub_key, message, signature, feed_cb=feed_cb)
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

_update_session: dict | None = None

def _valid_target_file(name):
    pass

def _abort_update_session(reason):
    pass

def _preallocate_tmp_file(tmp_name, size, chunk_size, num_chunks):
    pass

def _start_update_session(manifest):
    pass

def _append_update_chunk(chunk_msg):
    pass

async def _flash_message(text, seconds=5):
    pass

def _stage_update_session():
    pass

async def _apply_staged_update():
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

def _mark_boot_successful():
    pass

async def _feed_watchdog(wdt):
    while True:
        wdt.feed()
        # Feed at 1/4 of the timeout - if this task's turn is ever delayed
        # by other work, there's still margin before the hardware timer
        # actually expires.
        await asyncio.sleep(WDT_TIMEOUT_MS / 1000 / 4)

async def main():
    global lcd, mqtt, wdt

    i2c = I2C(0, sda=Pin(16), scl=Pin(17), freq=400000)
    lcd = LCD(i2c)
    lcd.message("System Startup.")
    _mark_boot_successful()

    # TODO: if WDT_ENABLE_FLAG in os.listdir(): get a handle to the
    # watchdog boot.py already armed (machine.WDT(timeout=WDT_TIMEOUT_MS)
    # again - it doesn't create a second one), store it in the global
    # `wdt`, and start _feed_watchdog(wdt) as a background task.
    #
    # TODO: connect_wifi() / get_mqtt_client() (same pattern as init.py),
    # tolerating failure - the lock must keep working without wifi. Send a
    # BOOT log message, then send_attestation() once per boot.
    #
    # If the MQTT client came up, start command_main() as a background
    # task (asyncio.create_task) so cloud pairing/unlock work even before
    # anyone touches the keypad. Then, if ROLLBACK_FLAG_FILE exists,
    # remove it and send an Action.ROLLBACK log (qos=1) - see
    # README.md#automatic-rollback step 4.
    #

    await keypad_main()

asyncio.run(main())
