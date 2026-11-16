# One-time script: generates this device's attestation identity keypair.
# Run this ONCE PER LOCK, directly ON the Pico (e.g. MicroPico: Run current
# file, or `mpremote run keygen_device.py`) - NOT with your computer's
# Python interpreter. The private key is generated here and never leaves
# the device: unlike keygen.py (the update-signing keypair, which has to
# be laptop-side since server.py itself runs there), there's no reason for
# this one to ever exist anywhere but on the device that signs with it.
#
# What happens:
#   1. A fresh keypair is generated on-device (ecdsa_verify.generate_keypair()).
#   2. The private half is written straight to this device's filesystem, as
#      DEVICE_PRIVATE_KEY_FILE - it stays there and is never printed/copied
#      out, not even transiently.
#   3. The public half is printed as hex, for YOU to copy by hand onto the
#      laptop that runs edge.py, as device_pubkey_<LOCKID>.der - the
#      out-of-band, physical-access trust-establishment step (same spirit
#      as ca.der/server_pubkey.der, just going the other direction).

import os
import ecdsa_verify

DEVICE_PRIVATE_KEY_FILE = "device_private_key.bin"  # must match common.py

if DEVICE_PRIVATE_KEY_FILE in os.listdir():
    print(f"{DEVICE_PRIVATE_KEY_FILE} already exists on this device - refusing to overwrite.")
    print("If you really mean to re-provision this device (its old identity")
    print("will stop being trusted by edge.py once you do), delete the file")
    print("first, then re-run this script.")
else:
    private_key, pubkey_bytes = ecdsa_verify.generate_keypair()

    with open(DEVICE_PRIVATE_KEY_FILE, "wb") as f:
        f.write(private_key.to_bytes(32, "big"))

    print(f"Attestation identity generated and saved to {DEVICE_PRIVATE_KEY_FILE}.")
    print("This file must never leave the device - do not copy it anywhere.")
    print()
    print("Copy the public key below to your laptop, next to edge.py, saved")
    print("as device_pubkey_<LOCKID>.der (use this device's LOCKID from")
    print("common.py):")
    print()
    print(pubkey_bytes.hex())
    print()
    print("On the laptop, one way to turn the hex above into that file:")
    print("  python -c \"open('device_pubkey_<LOCKID>.der','wb').write(bytes.fromhex('<paste the hex above>'))\"")
