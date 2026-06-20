import requests

from config import CLUBS_URL


def fetch_wallet_clubs(wallet):

    response = requests.get(
        CLUBS_URL,
        params={
            "walletAddress": wallet
        }
    )

    response.raise_for_status()

    return response.json()