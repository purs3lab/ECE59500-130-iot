from common import *
from init import *
from lcd import LCD
from machine import I2C, Pin

import asyncio
import aioble
import bluetooth
import ecdsa_verify

# How long a given CHALLENGE nonce stays valid before ble_unlock_main() gives
# up waiting for a response and rotates to a fresh one.
NONCE_LIFETIME_MS = 10_000

# Create and register the BLE service and its characteristics.

def verify_signature(pub_key, message, signature):
    try:
        return ecdsa_verify.verify(pub_key, message, signature)
    except Exception as e:
        print("Signature verification failed:", e)
        return False

async def pair_device():
    pass

async def ble_unlock_main():
    pass

async def keypad_main():
    pass

async def main():
    global lcd

    i2c = I2C(0, sda=Pin(16), scl=Pin(17), freq=400000)
    lcd = LCD(i2c)
    lcd.message("System Startup.")
    # Start ble service as a separate task so it can run concurrently with the keypad task.

    await keypad_main()

asyncio.run(main())