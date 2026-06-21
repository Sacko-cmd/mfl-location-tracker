from watchlist import load_watchlist


def get_club_list(user_id):
    watchlist = load_watchlist(user_id)
    return sorted(watchlist["club_ids"])
