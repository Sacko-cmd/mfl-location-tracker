from watchlist import load_watchlist, save_watchlist


def add_country(user_id, country):
    watchlist = load_watchlist(user_id)
    country = country.upper()
    if country not in watchlist["countries"]:
        watchlist["countries"].append(country)
        save_watchlist(user_id, watchlist)
        return True
    return False


def remove_country(user_id, country):
    watchlist = load_watchlist(user_id)
    country = country.upper()
    if country in watchlist["countries"]:
        watchlist["countries"].remove(country)
        save_watchlist(user_id, watchlist)
        return True
    return False
