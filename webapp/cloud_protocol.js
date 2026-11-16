export const TAG_CLOUD_PAIR = ':CLOUD_PAIR:';
export const TAG_CLOUD_UNLOCK = ':CLOUD_UNLOCK:';
export const TAG_APPLY_UPDATE = ':APPLY_UPDATE:';

export function cloudPairMessageBytes(lockId, code) {
  return concatBytes(utf8(lockId), utf8(TAG_CLOUD_PAIR), utf8(code));
}

export function cloudUnlockMessageBytes(lockId, nonceBytes, deviceIdBytes) {
  return concatBytes(utf8(lockId), utf8(TAG_CLOUD_UNLOCK), nonceBytes, deviceIdBytes);
}

export function applyUpdateMessageBytes(lockId, nonceBytes, deviceIdBytes) {
  return concatBytes(utf8(lockId), utf8(TAG_APPLY_UPDATE), nonceBytes, deviceIdBytes);
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
