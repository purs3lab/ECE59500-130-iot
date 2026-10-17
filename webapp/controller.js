// Cloud controller: register this phone with a lock, and unlock it,
// entirely through Firestore/MQTT (edge.py relaying both directions) - no
// Bluetooth involved. See README.md#controller-via-cloud.
//
// What's given vs. what you build (same split as part2's mobile.js): the
// five functions below - getOrCreateIdentity(), exportPublicKeyRaw(),
// signBytes(), submitCloudPairing(), cloudUnlock() - are the ones that
// actually execute README.md#controller-via-cloud's protocol and have to
// match the device byte-for-byte, so they're templated for you to fill in. Everything else
// (IndexedDB plumbing, rendering, the pairing modal) is given/working
// already, since it isn't part of the protocol itself.
import { initializeApp } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js';
import { getFirestore, doc, setDoc, onSnapshot } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js';
import {
  cloudPairMessageBytes, cloudUnlockMessageBytes, bytesToHex, hexToBytes,
} from './cloud_protocol.js';

// Firebase configuration - same project/config as app.js
const firebaseConfig = {
};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

// Same IndexedDB database/identity store as part2's mobile.js - a phone
// that already has an identity from part2 reuses that same key here
// instead of generating a second one. See README.md#controller-via-cloud,
// "Reusing the part2 phone identity".
const DB_NAME = 'secureiot-mobile';
const DB_VERSION = 2;
const STORE_IDENTITY = 'identity';
const STORE_MOBILE_LOCKS = 'locks';
const STORE_CLOUD_LOCKS = 'cloud_locks';

function openDb() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, DB_VERSION);
    req.onupgradeneeded = () => {
      const idb = req.result;
      if (!idb.objectStoreNames.contains(STORE_IDENTITY)) idb.createObjectStore(STORE_IDENTITY);
      if (!idb.objectStoreNames.contains(STORE_MOBILE_LOCKS)) idb.createObjectStore(STORE_MOBILE_LOCKS, { keyPath: 'lockId' });
      if (!idb.objectStoreNames.contains(STORE_CLOUD_LOCKS)) idb.createObjectStore(STORE_CLOUD_LOCKS, { keyPath: 'lockId' });
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

function idbGet(idb, store, key) {
  return new Promise((resolve, reject) => {
    const req = idb.transaction(store, 'readonly').objectStore(store).get(key);
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

function idbGetAll(idb, store) {
  return new Promise((resolve, reject) => {
    const req = idb.transaction(store, 'readonly').objectStore(store).getAll();
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

function idbPut(idb, store, value, key) {
  return new Promise((resolve, reject) => {
    const tx = idb.transaction(store, 'readwrite');
    const req = key !== undefined ? tx.objectStore(store).put(value, key) : tx.objectStore(store).put(value);
    req.onsuccess = () => resolve();
    req.onerror = () => reject(req.error);
  });
}

function idbDelete(idb, store, key) {
  return new Promise((resolve, reject) => {
    const req = idb.transaction(store, 'readwrite').objectStore(store).delete(key);
    req.onsuccess = () => resolve();
    req.onerror = () => reject(req.error);
  });
}

async function getOrCreateIdentity() {
}

async function exportPublicKeyRaw(publicKey) {
  // crypto.subtle.exportKey('raw', publicKey) -> Uint8Array
  // (0x04 || X(32) || Y(32) = 65 bytes).
}

async function signBytes(privateKey, messageBytes) {
  // crypto.subtle.sign({name: 'ECDSA', hash: 'SHA-256'}, privateKey,
  // messageBytes) -> Uint8Array (raw r||s, 64 bytes).
}

function sanitizeName(name) {
  return name.replace(/[\x00-\x1F\x7F]/g, '').trim().slice(0, 32) || 'Unnamed Phone';
}

function sanitizeLockId(lockId) {
  return (lockId || '').trim().toUpperCase().replace(/[^A-Z0-9_]/g, '').slice(0, 32);
}

const PAIRING_TIMEOUT_MS = 20000;
const UNLOCK_TIMEOUT_MS = 30000;

async function submitCloudPairing(lockId, code, displayName, onLog) {
}

async function cloudUnlock(record, onLog) {
}

async function forgetLock(lockId) {
  const idb = await openDb();
  await idbDelete(idb, STORE_CLOUD_LOCKS, lockId);
}

let savedLocks = [];
const statuses = {};

function log(msg, kind = 'info') {
  const el = document.getElementById('activity-log');
  const line = document.createElement('div');
  line.className = `log-line log-${kind}`;
  line.textContent = `[${new Date().toLocaleTimeString()}] ${msg}`;
  el.prepend(line);
  while (el.children.length > 200) el.removeChild(el.lastChild);
}

function setStatus(lockId, status) {
  statuses[lockId] = status;
  renderLocks();
}

async function loadSavedLocks() {
  const idb = await openDb();
  savedLocks = await idbGetAll(idb, STORE_CLOUD_LOCKS);
  renderLocks();
}

function renderLocks() {
  const container = document.getElementById('locks-list');
  container.innerHTML = '';

  if (savedLocks.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">☁️</div>
        <h3>No registered locks yet</h3>
        <p>Tap "Register New Lock" below and enter the code shown on the lock's screen.</p>
      </div>`;
    return;
  }

  for (const record of savedLocks) {
    const status = statuses[record.lockId] || 'idle';

    const card = document.createElement('div');
    card.className = 'lock-card mobile-lock-card';
    // lockId/name/status ultimately come from user input or a device-
    // originated value relayed through Firestore - build structure first,
    // fill in values as text, never interpolate into innerHTML.
    card.innerHTML = `
      <div class="mobile-lock-header">
        <h3></h3>
        <span class="status-badge"></span>
      </div>
      <div class="lock-info">
        <div><strong>Lock ID:</strong> <span class="lock-id-value"></span></div>
        <div><strong>Registered:</strong> <span class="paired-at-value"></span></div>
      </div>
      <div class="mobile-lock-actions">
        <button class="unlock-btn">☁️ Unlock</button>
        <button class="forget-btn">Forget</button>
      </div>
    `;

    card.querySelector('h3').textContent = record.name;
    const badge = card.querySelector('.status-badge');
    badge.textContent = { idle: 'Ready', unlocking: 'Unlocking…', unlocked: 'Unlocked', error: 'Error' }[status] || status;
    badge.classList.add(`badge-${status}`);
    card.querySelector('.lock-id-value').textContent = record.lockId;
    card.querySelector('.paired-at-value').textContent = new Date(record.pairedAt).toLocaleString();

    const unlockBtn = card.querySelector('.unlock-btn');
    unlockBtn.disabled = status === 'unlocking';
    unlockBtn.textContent = status === 'unlocking' ? 'Unlocking…' : (status === 'unlocked' ? '✅ Unlocked' : '☁️ Unlock');
    unlockBtn.onclick = () => doUnlock(record.lockId);

    card.querySelector('.forget-btn').onclick = () => onForget(record.lockId);

    container.appendChild(card);
  }
}

async function doUnlock(lockId) {
  const record = savedLocks.find(l => l.lockId === lockId);
  if (!record) return;
  setStatus(lockId, 'unlocking');
  try {
    const result = await cloudUnlock(record, log);
    if (result.success) {
      log(`${lockId} unlocked`, 'success');
      setStatus(lockId, 'unlocked');
      setTimeout(() => setStatus(lockId, 'idle'), 5000);
    } else {
      log(`${lockId} unlock rejected: ${result.reason}`, 'error');
      setStatus(lockId, 'idle');
    }
  } catch (e) {
    log(`Unlock failed for ${lockId}: ${e.message}`, 'error');
    setStatus(lockId, 'idle');
  }
}

async function onForget(lockId) {
  await forgetLock(lockId);
  savedLocks = savedLocks.filter(l => l.lockId !== lockId);
  delete statuses[lockId];
  renderLocks();
  // Local-only, same semantics as part2's mobile.js forgetLock() - the
  // lock itself still has this phone paired. There is deliberately no
  // remote/cloud "un-pair" command - see README.md#controller-via-cloud.
  log(`Forgot ${lockId} on this phone (the lock itself still has this phone registered)`);
}

function openPairingModal() {
  document.getElementById('pairing-modal').classList.remove('hidden');
  document.getElementById('pairing-error').classList.add('hidden');
  document.getElementById('pairing-lockid-input').value = '';
  document.getElementById('pairing-code-input').value = '';
  document.getElementById('pairing-name-input').value = '';
}

function closePairingModal() {
  document.getElementById('pairing-modal').classList.add('hidden');
}

async function confirmPairing() {
  const lockId = sanitizeLockId(document.getElementById('pairing-lockid-input').value);
  const code = document.getElementById('pairing-code-input').value.trim();
  const name = document.getElementById('pairing-name-input').value;
  const submitBtn = document.getElementById('pairing-submit-btn');
  const errorEl = document.getElementById('pairing-error');
  errorEl.classList.add('hidden');

  if (!lockId) {
    errorEl.textContent = 'Enter the Lock ID shown in your lock\'s setup (e.g. LOCK2).';
    errorEl.classList.remove('hidden');
    return;
  }
  if (!/^[0-9]{6}$/.test(code)) {
    errorEl.textContent = 'Code must be exactly 6 digits.';
    errorEl.classList.remove('hidden');
    return;
  }

  submitBtn.disabled = true;
  submitBtn.textContent = 'Registering…';
  try {
    const record = await submitCloudPairing(lockId, code, name, log);
    savedLocks = savedLocks.filter(l => l.lockId !== record.lockId);
    savedLocks.push(record);
    renderLocks();
    closePairingModal();
    log(`Registered with ${lockId}`, 'success');
  } catch (e) {
    errorEl.textContent = e.message;
    errorEl.classList.remove('hidden');
    log(`Pairing failed: ${e.message}`, 'error');
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = 'Register';
  }
}

window.openPairingModal = openPairingModal;
window.closePairingModal = closePairingModal;
window.confirmPairing = confirmPairing;

loadSavedLocks();
