from watchlist import (
    load_watchlist,
    save_watchlist
)


def enable_watchall():

    watchlist = load_watchlist()

    watchlist[
        "cities"
    ] = ["*"]

    save_watchlist(
        watchlist
    )