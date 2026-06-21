from watchlist import load_watchlist


def get_country_list(user_id):
    watchlist = load_watchlist(user_id)
    return sorted(watchlist["countries"])
