import {
  SERVICE_UUID, CHAR, ADV_NAME_PREFIX, lockIdFromDeviceName,
  pairMessageBytes, unlockMessageBytes, bytesToHex, hexToBytes,
  utf8, concatBytes,
} from './ble_protocol.js';

// Phone-side half of README.md#pairing / README.md#unlock. The four
// functions below are the ones that actually carry out those protocols and
// have to match the device byte-for-byte - fill them in per those sections
// and README.md#mobile-webapp.
//
// Everything else this page needs (rendering mobile.html, tracking
// connection/status state, the pairing modal flow, reconnect/liveness
// handling, wiring it all up in some init()) is on you and not prescribed
// here - there's no required shape for any of that, unlike the protocol
// itself.

// One ECDSA P-256 keypair for this phone, reused for every lock it pairs
// with (not a fresh one per lock). Generate it once with
// crypto.subtle.generateKey({name: 'ECDSA', namedCurve: 'P-256'}, false,
// ['sign', 'verify']), persist it somewhere that survives a reload (e.g.
// IndexedDB - a CryptoKey survives structured clone, no serialization
// needed), and return the same one on every later call. See "Web Crypto:
// the phone's identity" in README.md#mobile-webapp.
async function getOrCreateIdentity() {

}

// Connect to `device` and resolve every characteristic in CHAR (see
// ble_protocol.js) into a lookup object, e.g. via device.gatt.connect() ->
// getPrimaryService(SERVICE_UUID) -> getCharacteristic(uuid) per entry.
async function connectAndGetChars(device) {

}

// Full pairing write sequence from README.md#pairing: sign
// LOCKID + ":PAIR:" + code (pairMessageBytes) with this phone's identity,
// write the code/pubkey/name/signature to their characteristics
// (writeValueWithResponse), commit, and read back PAIR_STATUS.
async function submitPairing(session, code, displayName) {

}

// Phone side of README.md#unlock's challenge-response: sign
// LOCKID + ":UNLOCK:" + nonce + device_id (unlockMessageBytes - raw bytes,
// not string concatenation), write device_id || signature to
// UNLOCK_RESPONSE, and return the UNLOCK_STATUS result.
async function unlock(record, chars, nonce) {

}
