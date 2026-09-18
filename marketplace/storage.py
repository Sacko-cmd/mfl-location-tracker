import json
import threading

from config import MONITORS_FILE
from mfl_api import normalize_mfl_url

_lock = threading.Lock()


def load_monitors():
    with _lock:
        try:
            with open(MONITORS_FILE, encoding="utf8") as f:
                monitors = json.load(f)
            for monitor in monitors:
                if monitor.get("apiUrl"):
                    monitor["apiUrl"] = normalize_mfl_url(monitor["apiUrl"])
            return monitors
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
