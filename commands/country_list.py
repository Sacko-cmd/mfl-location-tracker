from watchlist import (
    load_watchlist
)


def get_country_list():

    watchlist = load_watchlist()

    return sorted(

        watchlist[
            "countries"
        ]

    )