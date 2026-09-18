import json
import os
import sqlite3
from contextlib import closing
from pathlib import Path

from config import DATABASE_FILE, WALLET_CACHE_FILE, DATA_DIR
from marketplace.storage import load_monitors
from tracker_status import get_tracker_status


def run_healthcheck():
    report = {"database": False, "wallet_cache": False}
    try:
        # Read-only: a health check must not create a missing database.
        with closing(sqlite3.connect(Path(DATABASE_FILE).resolve().as_uri() + "?mode=ro", uri=True)) as conn:
            conn.execute("SELECT 1 FROM transfers LIMIT 1")
        report["database"] = True
    except sqlite3.Error:
        pass
    try:
        with open(WALLET_CACHE_FILE, encoding="utf8") as f:
            report["wallet_cache"] = isinstance(json.load(f), dict)
    except (OSError, ValueError):
        pass

    tracker = get_tracker_status()
    monitors = load_monitors()
    active = [m for m in monitors if m.get("enabled")]
    report["tracker"] = tracker
    report["marketplace"] = {
        "configured": len(monitors),
        "enabled": len(active),
        "errors": sum(bool(m.get("lastError")) for m in active),
        "awaiting_first_check": sum(not m.get("lastCheck") for m in active),
    }
    report["storage"] = {
        "data_dir": str(DATA_DIR),
        "warning": (
            "Render local files are ephemeral. Set DATA_DIR to an attached persistent disk mount."
            if os.getenv("RENDER") and not os.getenv("DATA_DIR") else None
        ),
    }
    report["healthy"] = bool(
        report["database"] and tracker["healthy"]
        and not report["marketplace"]["errors"]
        and not report["marketplace"]["awaiting_first_check"]
    )
    return report
