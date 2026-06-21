from watchlist import load_watchlist, save_watchlist


def pause_notifications(user_id):
    watchlist = load_watchlist(user_id)
    watchlist["paused"] = True
    save_watchlist(user_id, watchlist)


def resume_notifications(user_id):
    watchlist = load_watchlist(user_id)
    watchlist["paused"] = False
    save_watchlist(user_id, watchlist)
