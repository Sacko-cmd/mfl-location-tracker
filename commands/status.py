from watchlist import load_watchlist


def get_status(user_id):
    watchlist = load_watchlist(user_id)
    return {
        "paused": watchlist["paused"],
        "cities": len(watchlist["cities"]),
        "countries": len(watchlist["countries"]),
        "club_ids": len(watchlist["club_ids"]),
    }
