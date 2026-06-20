from watchlist import (
    load_watchlist
)


def get_status():

    watchlist = load_watchlist()

    return {

        "paused": watchlist[
            "paused"
        ],

        "cities": len(
            watchlist[
                "cities"
            ]
        ),

        "countries": len(
            watchlist[
                "countries"
            ]
        ),

        "club_ids": len(
            watchlist[
                "club_ids"
            ]
        )

    }