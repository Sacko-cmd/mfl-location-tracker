"""In-process polling status; never persist errors containing webhook secrets."""
import threading
from datetime import datetime, timezone

from config import CHECK_INTERVAL_SECONDS, REQUEST_TIMEOUT_SECONDS

_lock = threading.Lock()
_state = {"last_attempt": None, "last_success": None, "last_error": None}


def poll_started():
    with _lock:
        _state["last_attempt"] = datetime.now(timezone.utc).isoformat()


def poll_finished(error=None):
    with _lock:
        _state["last_error"] = type(error).__name__ if error else None
        if error is None:
            _state["last_success"] = datetime.now(timezone.utc).isoformat()


def get_tracker_status():
    with _lock:
        result = dict(_state)
    success = result["last_success"]
    age = (datetime.now(timezone.utc) - datetime.fromisoformat(success)).total_seconds() if success else None
    result["healthy"] = bool(
        age is not None
        and age < max(3 * CHECK_INTERVAL_SECONDS, 2 * REQUEST_TIMEOUT_SECONDS)
        and result["last_error"] is None
    )
    return result
