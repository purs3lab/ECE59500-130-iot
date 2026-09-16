import machine
import json
import os
import hashlib
import asyncio
import aioble
import bluetooth

PIN_STORE = "pin_store.json"
PAIRED_DEVICE_STORE = "paired_device.json"

# Increment this for each lock deployed
LOCKID = "LOCK2"
MAX_BUFFER = 32

ADMIN_PANEL_ENTRY_CODE = "A"
ADMIN_PANEL_BACK = "B"
ADMIN_PANEL_FORWARD = "C"

# TODO: pick UUIDs for the service and each characteristic below - see
# "Picking UUIDs" in README.md#pairing for the 16-bit-vs-128-bit tradeoff and
# which ranges are safe to use. These must match ble_protocol.js's
# CHAR/SERVICE_UUID exactly, or the phone and device will disagree about what's what.
SERVICE_UUID = None
PAIR_CODE = None
PAIR_PUBKEY = None
PAIR_NAME = None
PAIR_SIG = None
PAIR_COMMIT = None
PAIR_STATUS = None
CHALLENGE = None
UNLOCK_RESPONSE = None
UNLOCK_STATUS = None

TAG_PAIR = ':PAIR:'
TAG_UNLOCK = ':UNLOCK:'

MAX_PAIR_ATTEMPTS = 3
MAX_PAIRED_DEVICES = 8

ADV_NAME_PREFIX = 'Yourid-'

_ble_service = aioble.Service(bluetooth.UUID(SERVICE_UUID))

# Build the nine characteristics below and attach them to _ble_service, using
# aioble.Characteristic(_ble_service, bluetooth.UUID(...), ...) /
# aioble.BufferedCharacteristic(...) for anything over 20 bytes. See "BLE/GATT
# background" in README.md#pairing for what write/capture/read/notify mean
# here and which characteristics need BufferedCharacteristic instead of the plain form.

def register_ble_service():
    # Must run before aioble.advertise() is ever called - characteristics
    # can't be added to a service after it's registered.
    aioble.register_services(_ble_service)


characters = [
    ["1","2","3","A"],
    ["4","5","6","B"],
    ["7","8","9","C"],
    ["*","0","#","D"]
]

buffer = []

row_pins = [6, 7, 8, 9]
col_pins = [10, 11, 12, 13]

rows = [machine.Pin(p, machine.Pin.OUT) for p in row_pins]
# Internal pull-down - no external resistor needed on the column lines
cols = [machine.Pin(p, machine.Pin.IN, machine.Pin.PULL_DOWN) for p in col_pins]

for r in rows:
    r.value(0)

def store_device_info(pubkey: bytes, name: str, sig: bytes) -> str | None:
    return device_id

def find_ble_device(device_id: str) -> dict | None:
    return None

def remove_paired_device(device_id: str) -> bool:
    return True

def get_paired_devices() -> list[dict]:
    return ids

def read_key():
    for i, r in enumerate(rows):
        r.value(1)
        for j, c in enumerate(cols):
            if c.value() == 1:
                r.value(0)
                return characters[i][j]
        r.value(0)
    return None

# Remaining functions from part1: pin_exists, store_pin, load_pin, remove_pin,
# constant_time_compare, validate_pin, get_input_string