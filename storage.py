import json

STATE_FILE = "ownership.json"


def _normalize_entry(club_id, club):
    return {
        "club_id": str(club_id),
        "city": club.get("city"),
        "country": club.get("country"),
        "missing_since": club.get("missing_since"),
        "missing_polls": club.get("missing_polls") or 0,
    }


def save_state(data):
    with open(STATE_FILE, "w", encoding="utf8") as f:
        json.dump(data, f, indent=2)


def load_state():
    try:
        with open(STATE_FILE, encoding="utf8") as f:
            raw = json.load(f)
    except FileNotFoundError:
        return {}

    state = {}
    for club_id, club in raw.items():
        state[str(club_id)] = _normalize_entry(club_id, club)
    return state


def build_pool_entry(club):
    return {
        "club_id": str(club["club_id"]),
        "city": club.get("city"),
        "country": club.get("country"),
        "missing_since": None,
        "missing_polls": 0,
    }
