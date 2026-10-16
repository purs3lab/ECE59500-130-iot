import paho.mqtt.client as mqtt
from google.cloud import firestore
import os
import json
import time
from datetime import datetime, timezone

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature
from cryptography.exceptions import InvalidSignature

GCP_CREDENTIALS_PATH = "NA"
MQTT_PASS = "NA"

# Domain-separation tag - must match TAG_ATTEST in common.py exactly, since
# the device and edge.py each independently build the same byte string and
# check it against the same signature.
TAG_ATTEST = b':ATTEST:'

assert GCP_CREDENTIALS_PATH != "NA", "Please set the GCP_CREDENTIALS_PATH variable with the correct path to your GCP credentials JSON file"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GCP_CREDENTIALS_PATH
db = firestore.Client()

def _load_known_devices():
    devices = {}
    prefix, suffix = "device_pubkey_", ".der"
    for name in os.listdir("."):
        if name.startswith(prefix) and name.endswith(suffix):
            lockid = name[len(prefix):-len(suffix)]
            with open(name, "rb") as f:
                devices[lockid] = f.read()
    return devices

KNOWN_DEVICES = _load_known_devices()

_last_attest = {}  # lockid -> (last accepted boot_count, uptime_ms), for staleness checks

def _verify_attestation(lockid, data):
    pass

def _is_safe_token(value, max_len):
    # Nothing proves an incoming message actually came from the lock it
    # claims to be, so don't trust lockid/action/device_id to be
    # well-formed before using them as Firestore document IDs/fields.
    return isinstance(value, str) and 0 < len(value) <= max_len and all(c.isalnum() or c == '_' for c in value)

# Cheap, code-only rate limit on the relay path: pairing_requests/commands
# accept writes from any browser with the page URL, no credential needed -
# this bounds how often a given lock's pending slot can be re-triggered,
# before a signature is ever checked. Not a replacement for the device's
# signature check - see README.md#controller-via-cloud's "Rate limiting" section.
_last_relay = {}  # (collection, lockid) -> time.monotonic() of last relay
RELAY_MIN_INTERVAL_S = 1.0

def _allow_relay(collection, lockid):
    key = (collection, lockid)
    now = time.monotonic()
    last = _last_relay.get(key)
    if last is not None and now - last < RELAY_MIN_INTERVAL_S:
        return False
    _last_relay[key] = now
    return True

def _on_pairing_request_snapshot(collection_snapshot, changes, read_time):
    pass

def _on_commands_snapshot(collection_snapshot, changes, read_time):
    pass

def _handle_pairing_status(lockid, data):
    pass

def _handle_challenge_or_result(lockid, data):
    pass

def _handle_lock_event(data):
    pass

def on_message(client, userdata, message):
    topic = message.topic
    try:
        data = json.loads(message.payload.decode())
        print(f"Received message on topic {topic}")

        if topic == 'secureiot/pico/data':
            _handle_lock_event(data)
        elif topic.startswith('secureiot/pico/pairing/status/'):
            _handle_pairing_status(topic.rsplit('/', 1)[-1], data)
        elif topic.startswith('secureiot/pico/challenge/'):
            _handle_challenge_or_result(topic.rsplit('/', 1)[-1], data)
        else:
            print(f"Message on unexpected topic: {topic}")
    except Exception as e:
        print(f"Error handling message on {topic}: {e}")

# Based on the version of paho-mqtt you are using, the client initialization may differ
client = mqtt.Client()
client.tls_set(ca_certs="ca.pem")
assert MQTT_PASS != "NA", "Please set the MQTT_PASS variable with the correct password"
client.username_pw_set("secure", MQTT_PASS)
client.on_message = on_message

client.connect("secure.cloud.shiftr.io", 8883)
client.subscribe("secureiot/pico/data")
client.subscribe("secureiot/pico/pairing/status/+")
client.subscribe("secureiot/pico/challenge/+")

db.collection('pairing_requests').on_snapshot(_on_pairing_request_snapshot)
db.collection('commands').on_snapshot(_on_commands_snapshot)

print("Firestore Bridge is running...")
client.loop_forever()
