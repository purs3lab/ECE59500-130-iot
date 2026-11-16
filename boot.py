# MicroPython always runs this before main.py, on every boot. Its only
# job is to detect a main.py that crashes or hangs before reaching a
# basic "alive" checkpoint (see main.py's _mark_boot_successful()) and
# restore the last-known-good backup

import os
import json
import machine

_BOOT_STATE_FILE = "boot_state.json"
_MAX_BOOT_ATTEMPTS = 3
_TARGET_FILE = "main.py"
_ROLLBACK_FLAG_FILE = "pending_rollback_report.flag"
# Same flag/timeout main.py uses (WDT_ENABLE_FLAG/WDT_TIMEOUT_MS) - same
# duplication reasoning as above.
_WDT_ENABLE_FLAG = "enable_wdt.flag"
_WDT_TIMEOUT_MS = 8000


def _load_attempts():
    pass


def _save_attempts(n):
    pass


_attempts = _load_attempts() + 1
_save_attempts(_attempts)

if _attempts > _MAX_BOOT_ATTEMPTS:
    # If _TARGET_FILE + ".bak" exists: restore it over _TARGET_FILE, reset
    # the attempt counter to 0, and write _ROLLBACK_FLAG_FILE so main.py can
    # report the rollback once it's back online.
    pass

# Start the watchdog timer here so any corrupt update will cause a rollback.
