from wallet_cache import (
    refresh_wallet_cache
)

from logger import (
    log_info,
    log_error
)


def run_wallet_refresh():

    try:

        log_info(
            "Refreshing wallet cache..."
        )

        refresh_wallet_cache()

        log_info(
            "Wallet refresh complete."
        )

    except Exception as e:

        log_error(
            f"Wallet refresh failed: {e}"
        )