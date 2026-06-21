from watchlist import load_watchlist, save_watchlist


def enable_watchall(user_id):
    watchlist = load_watchlist(user_id)
    watchlist["cities"] = ["*"]
    save_watchlist(user_id, watchlist)
