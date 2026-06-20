from watchlist import (
    load_watchlist,
    save_watchlist
)


def add_city(
        city
):

    watchlist = load_watchlist()

    if city not in watchlist["cities"]:

        watchlist["cities"].append(
            city
        )

        save_watchlist(
            watchlist
        )

        return True

    return False