import json
from datetime import datetime

POOL_LOG_FILE = "pool_changes.jsonl"


def log_pool_event(event):
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        **event,
    }
    with open(POOL_LOG_FILE, "a", encoding="utf8") as f:
        f.write(json.dumps(record) + "\n")


def read_pool_log(limit=15):
    try:
        with open(POOL_LOG_FILE, encoding="utf8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return []

    entries = []
    for line in lines[-limit:]:
        line = line.strip()
        if line:
            entries.append(json.loads(line))
    return list(reversed(entries))
