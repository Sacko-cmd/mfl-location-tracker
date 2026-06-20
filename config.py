import os

from dotenv import load_dotenv

load_dotenv()

CENTRAL_WALLET = "0xf45dfaa6233fae44"

FLOWTY_URL = f"https://api2.flowty.io/user/{CENTRAL_WALLET}"

LEADERBOARD_URL = (
    "https://z519wdyajg.execute-api.us-east-1.amazonaws.com/"
    "prod/leaderboards/users/global"
)

CLUBS_URL = (
    "https://z519wdyajg.execute-api.us-east-1.amazonaws.com/"
    "prod/clubs"
)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

CHECK_INTERVAL_SECONDS = 60
WALLET_REFRESH_HOURS = 6

DATABASE_FILE = "transfers.db"
WALLET_CACHE_FILE = "wallets.json"
WATCHLIST_FILE = "watchlist.json"

PORT = int(os.getenv("PORT", "10000"))
