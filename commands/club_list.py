from watchlist import (
    load_watchlist
)


def get_club_list():

    watchlist = load_watchlist()

    return sorted(

        watchlist[
            "club_ids"
        ]

    )