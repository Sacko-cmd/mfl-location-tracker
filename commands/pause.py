from watchlist import (
    load_watchlist,
    save_watchlist
)


def pause_notifications():

    watchlist = load_watchlist()

    watchlist["paused"] = True

    save_watchlist(
        watchlist
    )


def resume_notifications():

    watchlist = load_watchlist()

    watchlist["paused"] = False

    save_watchlist(
        watchlist
    )