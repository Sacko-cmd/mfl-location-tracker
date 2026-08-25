from config import CENTRAL_WALLET, CLUBS_URL
from logger import log_info
from mfl_api import mfl_get


def fetch_locations():
    log_info(f"Fetching pool wallet from MFL API: {CENTRAL_WALLET}")
    response = mfl_get(
        CLUBS_URL,
        params={"walletAddress": CENTRAL_WALLET},
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
