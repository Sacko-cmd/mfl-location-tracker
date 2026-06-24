import os

from dotenv import load_dotenv

load_dotenv()

CENTRAL_WALLET = os.getenv("CENTRAL_WALLET", "0xf45dfaa6233fae44")

LEADERBOARD_URL = (
    "https://z519wdyajg.execute-api.us-east-1.amazonaws.com/"
    "prod/leaderboards/users/global"
)

CLUBS_URL = (
    "https://z519wdyajg.execute-api.us-east-1.amazonaws.com/"
    "prod/clubs"
)

LISTINGS_URL = (
    "https://z519wdyajg.execute-api.us-east-1.amazonaws.com/"
    "prod/listings"
)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", "60"))
WALLET_REFRESH_HOURS = int(os.getenv("WALLET_REFRESH_HOURS", "12"))
REQUEST_TIMEOUT_SECONDS = 30
CONFIRM_MISSING_POLLS = int(os.getenv("CONFIRM_MISSING_POLLS", "2"))
MAX_DEPARTURE_AGE_HOURS = int(os.getenv("MAX_DEPARTURE_AGE_HOURS", "6"))

DATABASE_FILE = "transfers.db"
WALLET_CACHE_FILE = "wallets.json"
MONITORS_FILE = "monitors.json"
WATCHLIST_FILE = "watchlist.json"  # legacy; watchlists now live in SQLite

MAX_MONITORS_PER_INSTALL = int(os.getenv("MAX_MONITORS_PER_INSTALL", "5"))

PORT = int(os.getenv("PORT", "10000"))
