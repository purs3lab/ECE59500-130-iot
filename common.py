import machine
import network
import time
import json
import os
import asyncio
import ssl
from simple import MQTTClient, MQTTException

# Feel free to change the name and type of storage as needed
PIN_STORE = "pin_store.json"
BOOT_COUNT_STORE = "boot_count.json"
PAIRED_DEVICE_STORE = "paired_device.json"
# This device's own attestation identity key - see keygen_device.py and
# README.md#attestation. Unlike a signature-verification pubkey, this is a
# private key the device signs *with*, so it never leaves the device after
# provisioning.
DEVICE_PRIVATE_KEY_FILE = "device_private_key.bin"

MQTT_BROKER = "NA.cloud.shiftr.io"
# CLIENT_ID and LOCKID must both be unique per lock deployed - the broker
# will disconnect a device if another client connects with the same
# CLIENT_ID, so it's not enough to only change LOCKID. Change both when you
# flash your second Pico (see the README's second-device note).
CLIENT_ID = b"pico-w-1"
TOPIC = b"secureiot/pico/data"
LOCKID = "LOCK1"
MAX_WIFI_WAIT = 5
MAX_WIFI_RETRIES = 3

# Cloud pairing/unlock topics - see README.md#controller-via-cloud. Per-LOCKID
# (not the shared TOPIC above): a device only needs to see messages addressed to it.
PAIRING_REQUEST_TOPIC = ("secureiot/pico/pairing/request/" + LOCKID).encode()
PAIRING_STATUS_TOPIC = ("secureiot/pico/pairing/status/" + LOCKID).encode()
COMMAND_TOPIC = ("secureiot/pico/command/" + LOCKID).encode()
CHALLENGE_TOPIC = ("secureiot/pico/challenge/" + LOCKID).encode()

MQTT_PASS = "NA"
WIFI_SSID = "NA"
WIFI_PASS = "NA"

ADMIN_PANEL_ENTRY_CODE = "A"
ADMIN_PANEL_BACK = "B"
ADMIN_PANEL_FORWARD = "C"

# Domain-separation tags - must match cloud_protocol.js's TAG_CLOUD_PAIR/
# TAG_CLOUD_UNLOCK and edge.py's TAG_ATTEST exactly, since each side
# independently builds the same byte string and checks it against the same
# signature. See README.md#attestation / README.md#controller-via-cloud for
# what gets signed.
TAG_ATTEST = ':ATTEST:'
TAG_CLOUD_PAIR = ':CLOUD_PAIR:'
TAG_CLOUD_UNLOCK = ':CLOUD_UNLOCK:'

MAX_PAIR_ATTEMPTS = 3
MAX_PAIRED_DEVICES = 8

current_wifi_retries = 0
wifi_status = False
mqtt_status = False

characters = [
    ["1","2","3","A"],
    ["4","5","6","B"],
    ["7","8","9","C"],
    ["*","0","#","D"]
]

# Update based on your wiring
row_pins = [6, 7, 8, 9]
# Update based on your wiring
col_pins = [10, 11, 12, 13]

rows = [machine.Pin(p, machine.Pin.OUT) for p in row_pins]
# Internal pull-down - no external resistor needed on the column lines
cols = [machine.Pin(p, machine.Pin.IN, machine.Pin.PULL_DOWN) for p in col_pins]

# Initialize all row pins to low
for r in rows:
    r.value(0)

class Action():
    UNLOCK = 1
    # Lock action always happens automatically after a delay
    LOCK = 2
    SET_PIN = 3
    RESET_PIN = 4
    # Used to show that the system is starting up
    BOOT = 5
    # General warning message
    WARN = 6
    # Proof-of-identity signal, sent once per boot - see README.md#attestation
    # and send_attestation() in main.py.
    ATTEST = 7
    # Admin panel access (keypad-gated, PIN re-checked at entry)
    ADMIN_PANEL = 8
    # Cloud-controller pairing/removal/unlock - see README.md#controller-via-cloud
    PAIR_DEVICE = 9
    UNPAIR_DEVICE = 10
    CLOUD_UNLOCK = 11

def action_name(value):
    for name, val in Action.__dict__.items():
        if val == value:
            return name
    return "UNKNOWN"

def store_device_info(pubkey: bytes, name: str, sig: bytes, via: str) -> str | None:
    pass

# Look up a paired controller by device_id (used by cloud unlock and unpairing).
def find_paired_device(device_id: str) -> dict | None:
    pass

def remove_paired_device(device_id: str) -> bool:
    pass

def get_paired_devices() -> list[dict]:
    pass

def load_device_private_key() -> int:
    with open(DEVICE_PRIVATE_KEY_FILE, "rb") as f:
        return int.from_bytes(f.read(), "big")

def next_boot_count() -> int:
    # Persisted, monotonically-increasing counter - gives edge.py something
    # to check freshness against (see _verify_attestation() in edge.py).
    if BOOT_COUNT_STORE not in os.listdir():
        count = 0
    else:
        with open(BOOT_COUNT_STORE, "r") as f:
            try:
                count = json.load(f).get("count", 0)
            except ValueError:
                count = 0
    count += 1
    with open(BOOT_COUNT_STORE, "w") as f:
        json.dump({"count": count}, f)
    return count

# Remaining functions from part1: pin_exists, store_pin, load_pin,
# remove_pin, constant_time_compare, validate_pin, get_input_string - bring
# your implementations forward, they don't change here.

# Read the current key pressed on the keypad
def read_key():
    for i, r in enumerate(rows):
        r.value(1)
        for j, c in enumerate(cols):
            if c.value() == 1:
                r.value(0)
                return characters[i][j]
        r.value(0)
    return None

# NOTE: connect_wifi/get_mqtt_client are async here (unlike earlier parts) -
# part3's cloud-controller addition needs a background task that polls
# check_msg() independently of the keypad (see command_main() in main.py),
# which needs cooperative concurrency. Wrap your part2 logic in async
# def/await accordingly; asyncio.sleep(...) in place of any blocking wait.

async def connect_wifi():
    # Activate the interface and connect to the AP. Don't retry forever -
    # cap it with MAX_WIFI_RETRIES/MAX_WIFI_WAIT so the lock keeps working
    # as a standalone keypad lock even when wifi is unavailable.

    wlan = network.WLAN(network.STA_IF)
    # Activate the interface and connect to the AP

    # Wait until connected, using asyncio.sleep(...) rather than a blocking
    # sleep, so other tasks (the keypad loop, command_main()) keep running.
    pass

async def get_mqtt_client() -> MQTTClient:
    # Sync time with some ntp server (see the ntptime library) - without a
    # correct clock, certificate validation below will fail. If sync fails,
    # log it clearly and continue without authentication (see README.md#mqtt
    # for why that fallback is a real security trade-off).

    ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    # Load ca.der (converted from the broker's ca.pem, see README.md#mqtt)
    # and use authentication only if time sync was successful:
    # ssl_ctx.verify_mode =
    # ssl_ctx.load_verify_locations(cadata=...)
    client = MQTTClient(
        CLIENT_ID,
        MQTT_BROKER,  # MQTT broker address. E.g., test.cloud.shiftr.io
        port=8883,
        user="secure",  # shiftr username - see README.md#mqtt
        password=MQTT_PASS,
        ssl=ssl_ctx,
    )
    client.connect()
    return client
