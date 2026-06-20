import time

from config import CHECK_INTERVAL_SECONDS, WALLET_REFRESH_HOURS
from logger import log_error, log_info
from transfer_detector import detect_transfers
from wallet_cache import refresh_wallet_cache


def run():
    last_wallet_refresh = time.time()

    while True:
        now = time.time()

        if now - last_wallet_refresh > WALLET_REFRESH_HOURS * 3600:
            log_info("Refreshing wallet cache...")
            try:
                refresh_wallet_cache()
                last_wallet_refresh = now
            except Exception as e:
                log_error(f"Wallet cache refresh failed: {e}")

        try:
            detect_transfers()
        except Exception as e:
            log_error(f"Transfer check failed: {e}")

        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    run()
