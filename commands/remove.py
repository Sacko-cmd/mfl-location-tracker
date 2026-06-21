from watchlist import load_watchlist, save_watchlist


def remove_city(user_id, city):
    watchlist = load_watchlist(user_id)
    if city in watchlist["cities"]:
        watchlist["cities"].remove(city)
        save_watchlist(user_id, watchlist)
        return True
    return False
