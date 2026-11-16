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
DEVICE_PRIVATE_KEY_FILE = "device_private_key.bin"
BOOT_STATE_FILE = "boot_state.json"
INSTALLED_VERSIONS_STORE = "installed_versions.json"
STAGED_UPDATE_STORE = "staged_update.json"
SERVER_PUBKEY_FILE = "server_pubkey.der"

MQTT_BROKER = "NA.cloud.shiftr.io"
CLIENT_ID = b"pico-w-1"
TOPIC = b"secureiot/pico/data"
LOCKID = "LOCK1"
MAX_WIFI_WAIT = 5
MAX_WIFI_RETRIES = 3

PAIRING_REQUEST_TOPIC = ("secureiot/pico/pairing/request/" + LOCKID).encode()
PAIRING_STATUS_TOPIC = ("secureiot/pico/pairing/status/" + LOCKID).encode()
COMMAND_TOPIC = ("secureiot/pico/command/" + LOCKID).encode()
CHALLENGE_TOPIC = ("secureiot/pico/challenge/" + LOCKID).encode()

UPDATE_TOPIC = ("secureiot/pico/update/" + LOCKID).encode()
UPDATE_TOPIC_WILDCARD = UPDATE_TOPIC + b"/#"
UPDATE_MANIFEST_TOPIC = UPDATE_TOPIC + b"/manifest"
UPDATE_CHUNK_TOPIC_PREFIX = UPDATE_TOPIC + b"/chunk/"

MQTT_USER = "NA"
MQTT_PASS = "NA"
WIFI_SSID = "NA"
WIFI_PASS = "NA"

ADMIN_PANEL_ENTRY_CODE = "A"
ADMIN_PANEL_BACK = "B"
ADMIN_PANEL_FORWARD = "C"


TAG_ATTEST = ':ATTEST:'
TAG_CLOUD_PAIR = ':CLOUD_PAIR:'
TAG_CLOUD_UNLOCK = ':CLOUD_UNLOCK:'
TAG_APPLY_UPDATE = ':APPLY_UPDATE:'

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
    # Proof-of-identity signal, sent once per boot - see part3's
    # README.md#attestation and send_attestation() in main.py.
    ATTEST = 7
    # Admin panel access (keypad-gated, PIN re-checked at entry)
    ADMIN_PANEL = 8
    # Cloud-controller pairing/removal/unlock - see part3's README.md#controller-via-cloud
    PAIR_DEVICE = 9
    UNPAIR_DEVICE = 10
    CLOUD_UNLOCK = 11
    # Remote update related actions - see README.md#remote-updates / README.md#automatic-rollback
    UPDATE = 12
    ROLLBACK = 13
    # Verified+staged, awaiting a signed APPLY_UPDATE - distinct from UPDATE
    # (which means "applied") so the dashboard can tell "update ready" from
    # "update installed".
    UPDATE_STAGED = 14

def action_name(value):
    for name, val in Action.__dict__.items():
        if val == value:
            return name
    return "UNKNOWN"

def store_device_info(pubkey: bytes, name: str, sig: bytes, via: str) -> str | None:
    pass

# Name carried over from part2, but this should be used for cloud pairing/unpairing as well.
def find_ble_device(device_id: str) -> dict | None:
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

def get_installed_version(target_file: str) -> int:
    pass

def set_installed_version(target_file: str, version: int):
    pass

def get_staged_update() -> dict | None:
    pass

def set_staged_update(target_file: str, version: int, sha256_hex: str):
    pass

def clear_staged_update():
    pass

def load_server_pubkey() -> bytes:
    with open(SERVER_PUBKEY_FILE, "rb") as f:
        return f.read()

# Remaining functions from part1: pin_exists, store_pin, load_pin,
# remove_pin, constant_time_compare, validate_pin, get_input_string - bring
# your implementations forward, they don't change here.
#
# Also bring forward your send_mqtt_message()/_craft_message() from part3 -
# add a qos: int = 0 parameter that gets passed through to publish(). You'll
# need qos=1 for the one MQTT message in this part that matters most and
# has the least room for error (see README.md#remote-updates).

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


async def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    pass

async def get_mqtt_client() -> MQTTClient:
    ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    # Load ca.der (converted from the broker's ca.pem, see part3's
    # README.md#mqtt) and use authentication only if time sync was successful:
    # ssl_ctx.verify_mode =
    # ssl_ctx.load_verify_locations(cadata=...)
    client = MQTTClient(
        CLIENT_ID,
        MQTT_BROKER,
        port=8883,
        user=MQTT_USER,
        password=MQTT_PASS,
        ssl=ssl_ctx,
    )
    client.connect()
    return client
