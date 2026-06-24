import json
import threading

from config import MONITORS_FILE

_lock = threading.Lock()


def load_monitors():
    with _lock:
        try:
            with open(MONITORS_FILE, encoding="utf8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []


def save_monitors(monitors):
    with _lock:
        with open(MONITORS_FILE, "w", encoding="utf8") as f:
            json.dump(monitors, f, indent=2)


def ensure_monitors_file():
    with _lock:
        try:
            with open(MONITORS_FILE, encoding="utf8") as f:
                json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            with open(MONITORS_FILE, "w", encoding="utf8") as f:
                json.dump([], f)
