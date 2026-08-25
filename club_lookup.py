from config import CLUBS_URL
from mfl_api import mfl_get


def fetch_wallet_clubs(wallet):
    response = mfl_get(
        CLUBS_URL,
        params={"walletAddress": wallet},
    )
    response.raise_for_status()
    return response.json()


def fetch_club_by_id(club_id):
    response = mfl_get(
        f"{CLUBS_URL}/{club_id}",
    )
    response.raise_for_status()
    return response.json()
