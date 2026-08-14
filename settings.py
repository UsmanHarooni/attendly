import hashlib
import json
import secrets

from paths import DATA_DIR

SETTINGS_PATH = DATA_DIR / "settings.json"

DEFAULTS = {
    "marking_mode": "daily",
    "admin_pin": None,
    "last_backup": None,
}
VALID_MODES = ("daily", "session")
DEFAULT_PIN = "1234"


def _load():
    if not SETTINGS_PATH.exists():
        return dict(DEFAULTS)
    try:
        data = json.loads(SETTINGS_PATH.read_text())
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULTS)
    return {**DEFAULTS, **data}


def _save(data):
    DATA_DIR.mkdir(exist_ok=True)
    SETTINGS_PATH.write_text(json.dumps(data, indent=2))


def get_marking_mode():
    mode = _load().get("marking_mode")
    return mode if mode in VALID_MODES else DEFAULTS["marking_mode"]


def set_marking_mode(mode):
    if mode not in VALID_MODES:
        raise ValueError(f"Invalid marking mode: {mode}")
    data = _load()
    data["marking_mode"] = mode
    _save(data)


def _pin_hash(pin):
    return hashlib.sha256(f"facetrack::{pin}".encode()).hexdigest()


def verify_admin_pin(pin):
    expected = _load().get("admin_pin") or _pin_hash(DEFAULT_PIN)
    return secrets.compare_digest(expected, _pin_hash(pin.strip()))


def has_custom_pin():
    return bool(_load().get("admin_pin"))


def set_admin_pin(pin):
    if not pin or len(pin) < 4:
        raise ValueError("PIN must be at least 4 characters")
    data = _load()
    data["admin_pin"] = _pin_hash(pin)
    _save(data)


def last_backup():
    return _load().get("last_backup")


def set_last_backup(date_str):
    data = _load()
    data["last_backup"] = date_str
    _save(data)