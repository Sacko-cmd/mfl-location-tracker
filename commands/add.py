from watchlist import load_watchlist, save_watchlist


def add_city(user_id, city):
    watchlist = load_watchlist(user_id)
    if city not in watchlist["cities"]:
        watchlist["cities"].append(city)
        save_watchlist(user_id, watchlist)
        return True
    return False
