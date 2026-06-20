import json

from config import WALLET_CACHE_FILE
from leaderboard_scraper import get_all_managers


def refresh_wallet_cache():
    managers = get_all_managers()

    wallets = {}
    for manager in managers:
        wallets[manager["walletAddress"]] = manager["name"]

    with open(WALLET_CACHE_FILE, "w", encoding="utf8") as f:
        json.dump(wallets, f, indent=2)


def load_wallet_cache():
    try:
        with open(WALLET_CACHE_FILE, encoding="utf8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
