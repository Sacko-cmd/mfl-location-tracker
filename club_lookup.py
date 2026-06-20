import requests

from config import CLUBS_URL, REQUEST_TIMEOUT_SECONDS


def fetch_wallet_clubs(wallet):
    response = requests.get(
        CLUBS_URL,
        params={"walletAddress": wallet},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()
