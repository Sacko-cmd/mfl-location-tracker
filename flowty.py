import requests

from config import FLOWTY_URL, REQUEST_TIMEOUT_SECONDS
from logger import log_info


def fetch_central_wallet():
    log_info(f"Fetching Flowty wallet: {FLOWTY_URL}")
    response = requests.get(FLOWTY_URL, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.json()


def fetch_locations():
    data = fetch_central_wallet()

    locations = {}

    for nft in data["nfts"]:
        if nft["contractName"] != "MFLClub":
            continue

        traits = nft["nftView"]["traits"]["traits"]

        city = None
        country = None

        for trait in traits:
            if trait["name"] == "city":
                city = trait["value"]
            elif trait["name"] == "country":
                country = trait["value"]

        locations[nft["id"]] = {
            "club_id": nft["id"],
            "city": city,
            "country": country,
        }

    log_info(f"Loaded {len(locations)} locations from Flowty.")
    return locations
