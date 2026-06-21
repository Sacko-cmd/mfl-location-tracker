from flowty import fetch_locations
from storage import load_state


def get_pending_departures():
    previous = load_state()
    current = fetch_locations()

    pending = []
    for club_id, club in previous.items():
        if club_id not in current:
            pending.append(
                {
                    "club_id": club_id,
                    "city": club.get("city"),
                    "country": club.get("country"),
                }
            )

    return pending
