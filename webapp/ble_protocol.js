// TODO: fill these in to match the UUIDs you picked in common.py exactly -
// see "Picking UUIDs" in README.md#pairing. Web Bluetooth accepts plain
// numbers for 16-bit UUIDs (e.g. 0xff00) and expands them to the full UUID itself.
export const SERVICE_UUID = null;

export const CHAR = {
  PAIR_CODE:   null, // write: ASCII digits, e.g. b"123456" (6 bytes)
  PAIR_PUBKEY: null, // write: raw uncompressed EC point, 0x04||X||Y (65 bytes)
  PAIR_NAME:   null, // write: UTF-8 display name, capped length
  PAIR_SIG:    null, // write: raw r||s signature (64 bytes)
  PAIR_COMMIT: null, // write: empty value - triggers server-side validation of the above
  PAIR_STATUS: null, // read after commit: JSON, must carry device_id on success (see README.md#pairing)

  // --- Unlock (fresh challenge-response every time, works any time the
  // device is powered - not gated by pairing mode) ---
  CHALLENGE:       null, // read: new random 32-byte nonce every read, scoped to this connection
  UNLOCK_RESPONSE: null, // write: device_id (8 raw bytes) || sig (raw r||s, 64 bytes) = 72 bytes
  UNLOCK_STATUS:   null, // read after write: JSON
};

export const ADV_NAME_PREFIX = 'Yourid-';

export function lockIdFromDeviceName(name) {
  if (!name || !name.startsWith(ADV_NAME_PREFIX)) return null;
  return name.slice(ADV_NAME_PREFIX.length);
}

export const TAG_PAIR = ':PAIR:';
export const TAG_UNLOCK = ':UNLOCK:';

export function pairMessageBytes(lockId, code) {
  return concatBytes(utf8(lockId), utf8(TAG_PAIR), utf8(code));
}

export function unlockMessageBytes(lockId, nonceBytes, deviceIdBytes) {
  return concatBytes(utf8(lockId), utf8(TAG_UNLOCK), nonceBytes, deviceIdBytes);
}

export function utf8(str) {
  return new TextEncoder().encode(str);
}

export function concatBytes(...parts) {
  const total = parts.reduce((n, p) => n + p.length, 0);
  const out = new Uint8Array(total);
  let offset = 0;
  for (const p of parts) {
    out.set(p, offset);
    offset += p.length;
  }
  return out;
}

export function bytesToHex(bytes) {
  return Array.from(bytes).map(b => b.toString(16).padStart(2, '0')).join('');
}

export function hexToBytes(hex) {
  const out = new Uint8Array(hex.length / 2);
  for (let i = 0; i < out.length; i++) {
    out[i] = parseInt(hex.substr(i * 2, 2), 16);
  }
  return out;
}
