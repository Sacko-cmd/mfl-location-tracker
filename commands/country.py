from watchlist import (
    load_watchlist,
    save_watchlist
)


def add_country(
        country
):

    watchlist = load_watchlist()

    country = country.upper()

    if (
        country
        not in
        watchlist["countries"]
    ):

        watchlist[
            "countries"
        ].append(
            country
        )

        save_watchlist(
            watchlist
        )

        return True

    return False


def remove_country(
        country
):

    watchlist = load_watchlist()

    country = country.upper()

    if (
        country
        in
        watchlist["countries"]
    ):

        watchlist[
            "countries"
        ].remove(
            country
        )

        save_watchlist(
            watchlist
        )

        return True

    return False