import threading

from config import DISCORD_TOKEN
from database import initialise_database
from logger import log_error, log_info
from scheduler import run
from wallet_refresh import run_wallet_refresh


def start_discord_bot():
    if not DISCORD_TOKEN:
        log_info("DISCORD_TOKEN not set; skipping Discord bot commands.")
        return

    try:
        from discord_bot import run_bot
    except Exception as e:
        log_error(f"Discord bot unavailable: {e}")
        return

    log_info("Starting Discord bot...")
    threading.Thread(target=run_bot, daemon=True).start()


def start_marketplace():
    from marketplace.storage import ensure_monitors_file
    from marketplace.scheduler import schedule_all

    ensure_monitors_file()
    log_info("Starting marketplace monitors...")
    schedule_all()


def start_wallet_refresh():
    def worker():
        log_info("Wallet refresh thread started.")
        run_wallet_refresh()
        log_info("Wallet refresh thread finished.")

    threading.Thread(target=worker, daemon=True).start()


def startup():
    log_info("Starting MFL tracker...")

    try:
        log_info("Initialising database...")
        initialise_database()
        log_info("Database OK")

        start_discord_bot()
        start_wallet_refresh()
        start_marketplace()

        log_info("Starting scheduler...")
        run()

    except Exception as e:
        log_error(f"STARTUP FAILED: {repr(e)}")
        raise


if __name__ == "__main__":
    startup()
