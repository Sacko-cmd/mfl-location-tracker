import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

CENTRAL_WALLET = os.getenv("CENTRAL_WALLET", "0xf45dfaa6233fae44")

MFL_API_BASE_URL = os.getenv("MFL_API_BASE_URL", "https://api.playmfl.com").rstrip("/")
LEADERBOARD_URL = f"{MFL_API_BASE_URL}/leaderboards/users/global"
CLUBS_URL = f"{MFL_API_BASE_URL}/clubs"
LISTINGS_URL = f"{MFL_API_BASE_URL}/listings"

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", "60"))
WALLET_REFRESH_HOURS = int(os.getenv("WALLET_REFRESH_HOURS", "12"))
REQUEST_TIMEOUT_SECONDS = 30
CONFIRM_MISSING_POLLS = int(os.getenv("CONFIRM_MISSING_POLLS", "2"))
MAX_DEPARTURE_AGE_HOURS = int(os.getenv("MAX_DEPARTURE_AGE_HOURS", "6"))

DATA_DIR = Path(os.getenv("DATA_DIR", "."))
DATA_DIR.mkdir(parents=True, exist_ok=True)


def data_file(name):
    return str(DATA_DIR / name)


DATABASE_FILE = data_file("transfers.db")
WALLET_CACHE_FILE = data_file("wallets.json")
MONITORS_FILE = data_file("monitors.json")
WATCHLIST_FILE = data_file("watchlist.json")  # legacy; watchlists now live in SQLite

MAX_MONITORS_PER_INSTALL = int(os.getenv("MAX_MONITORS_PER_INSTALL", "5"))

PORT = int(os.getenv("PORT", "10000"))
