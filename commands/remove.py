from watchlist import (
    load_watchlist,
    save_watchlist
)


def remove_city(
        city
):

    watchlist = load_watchlist()

    if city in watchlist["cities"]:

        watchlist["cities"].remove(
            city
        )

        save_watchlist(
            watchlist
        )

        return True

    return False