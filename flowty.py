import requests

from config import CENTRAL_WALLET, CLUBS_URL, REQUEST_TIMEOUT_SECONDS
from logger import log_info


def fetch_locations():
    log_info(f"Fetching pool wallet from MFL API: {CENTRAL_WALLET}")
    response = requests.get(
        CLUBS_URL,
        params={"walletAddress": CENTRAL_WALLET},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    data = response.json()

    locations = {}
    for item in data:
        club = item["club"]
        club_id = str(club["id"])
        locations[club_id] = {
            "club_id": club_id,
            "city": club.get("city"),
            "country": club.get("country"),
        }

    log_info(f"Loaded {len(locations)} locations from pool wallet.")
    return locations
