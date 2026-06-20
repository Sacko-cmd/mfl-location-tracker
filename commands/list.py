from watchlist import (
    load_watchlist
)


def list_watchlist():

    watchlist = load_watchlist()

    cities = watchlist["cities"]

    countries = (
        watchlist["countries"]
    )

    club_ids = (
        watchlist["club_ids"]
    )

    return {

        "cities": cities,

        "countries": countries,

        "club_ids": club_ids,

        "paused": watchlist[
            "paused"
        ]

    }