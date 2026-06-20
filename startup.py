import threading

from config import DISCORD_TOKEN
from database import initialise_database
from discord_bot import run_bot
from logger import log_error, log_info
from scheduler import run
from wallet_refresh import run_wallet_refresh
from watchlist import create_watchlist


def start_discord_bot():
    if not DISCORD_TOKEN:
        log_info("DISCORD_TOKEN not set; skipping Discord bot commands.")
        return

    log_info("Starting Discord bot...")
    threading.Thread(target=run_bot, daemon=True).start()


def startup():
    log_info("Starting MFL tracker...")

    try:
        log_info("Initialising database...")
        initialise_database()
        log_info("Database OK")

        log_info("Creating watchlist...")
        create_watchlist()
        log_info("Watchlist OK")

        start_discord_bot()

        log_info("Refreshing wallets...")
        run_wallet_refresh()
        log_info("Wallet refresh OK")

        log_info("Starting scheduler...")
        run()

    except Exception as e:
        log_error(f"STARTUP FAILED: {repr(e)}")
        raise


if __name__ == "__main__":
    startup()
