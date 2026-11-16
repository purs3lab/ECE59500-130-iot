# One-time script: generates the update-signing ECDSA P-256 keypair.
# Run this once per lock deployment, before running server.py for the
# first time.

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

private_key = ec.generate_private_key(ec.SECP256R1())

with open("server_private_key.pem", "wb") as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ))

pubkey_raw = private_key.public_key().public_bytes(
    encoding=serialization.Encoding.X962,
    format=serialization.PublicFormat.UncompressedPoint,
)

with open("server_pubkey.der", "wb") as f:
    f.write(pubkey_raw)

print("Generated update-signing keypair:")
print("  server_private_key.pem  (keep secret, stays on the laptop)")
print(f"  server_pubkey.der       ({len(pubkey_raw)} bytes, copy to the Pico as server_pubkey.der)")
