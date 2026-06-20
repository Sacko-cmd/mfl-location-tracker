import json

from config import WATCHLIST_FILE


DEFAULT_WATCHLIST = {
    "cities": ["*"],
    "countries": [],
    "club_ids": [],
    "paused": False
}


def create_watchlist():

    try:

        with open(WATCHLIST_FILE):

            pass

    except FileNotFoundError:

        save_watchlist(DEFAULT_WATCHLIST)


def load_watchlist():

    with open(
        WATCHLIST_FILE,
        encoding="utf8"
    ) as f:

        return json.load(f)


def save_watchlist(data):

    with open(
        WATCHLIST_FILE,
        "w",
        encoding="utf8"
    ) as f:

        json.dump(
            data,
            f,
            indent=2
        )


def should_notify(
        city,
        country,
        club_id
):

    watchlist = load_watchlist()

    if watchlist["paused"]:

        return False

    if "*" in watchlist["cities"]:

        return True

    if city in watchlist["cities"]:

        return True

    if country in watchlist["countries"]:

        return True

    if str(club_id) in watchlist["club_ids"]:

        return True

    return False