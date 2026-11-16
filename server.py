import paho.mqtt.client as mqtt
import sys
import os
import json
import base64
import struct
import hashlib

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature

VERSION_STATE_FILE = "server_versions.json"

def last_push(lock_id, target_file):
    # What you know about the previous successful push for this (lock,
    # file) pair - both the version to increment from (replaces
    # next_version() from earlier drafts of this file), and its
    # num_chunks, which is what lets a later run clear any now-orphaned
    # retained chunk topics a smaller replacement file wouldn't otherwise
    # overwrite (see the retained-chunk cleanup note below, right before
    # publishing). Persist both in VERSION_STATE_FILE, same as before.
    pass

def save_push(lock_id, target_file, version, num_chunks):
    pass

if len(sys.argv) != 3:
    print("Usage: python server.py <LOCKID> <update_file>")
    sys.exit(1)

lock_id = sys.argv[1]
update_file = sys.argv[2]
topic_base = f"secureiot/pico/update/{lock_id}"
manifest_topic = f"{topic_base}/manifest"
def chunk_topic(seq):
    return f"{topic_base}/chunk/{seq}"

if not update_file.endswith(".py"):
    print("Error: update_file must be a .py file")
    sys.exit(1)

if not os.path.exists(update_file):
    print(f"Error: {update_file} does not exist")
    sys.exit(1)

with open(update_file, "rb") as f:
    content = f.read()

target_file = os.path.basename(update_file)
last_version, last_num_chunks = last_push(lock_id, target_file)
version = last_version + 1
size = len(content)
file_hash = hashlib.sha256(content).digest()
# Not a protocol requirement - any chunk_size works as long as it's kept
# consistent with num_chunks below. 512 just keeps each MQTT message small.
chunk_size = 512
num_chunks = (size + chunk_size - 1) // chunk_size

with open("server_private_key.pem", "rb") as f:
    private_key = serialization.load_pem_private_key(f.read(), password=None)
if not isinstance(private_key, ec.EllipticCurvePrivateKey):
    raise TypeError("server_private_key.pem is not an EC private key - re-run keygen.py")

message = target_file.encode() + struct.pack(">I", version) + file_hash + struct.pack(">I", size)
der_sig = private_key.sign(message, ec.ECDSA(hashes.SHA256()))
r, s = decode_dss_signature(der_sig)
signature = r.to_bytes(32, "big") + s.to_bytes(32, "big")

manifest = {
    "type": "update_manifest",
    "target_file": target_file,
    "version": version,
    "sha256": file_hash.hex(),
    "size": size,
    "chunk_size": chunk_size,
    "num_chunks": num_chunks,
    "signature": signature.hex(),
}

client = mqtt.Client()
client.tls_set(ca_certs="ca.pem")
client.username_pw_set("XXX", "XXX")
client.connect("XXX.cloud.shiftr.io", 8883)
client.loop_start()

# Your code here

client.loop_stop()
client.disconnect()
print("Update published.")
