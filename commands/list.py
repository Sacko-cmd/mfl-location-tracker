from watchlist import load_watchlist


def list_watchlist(user_id):
    watchlist = load_watchlist(user_id)
    return {
        "cities": watchlist["cities"],
        "countries": watchlist["countries"],
        "club_ids": watchlist["club_ids"],
        "paused": watchlist["paused"],
    }
