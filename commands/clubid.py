from watchlist import (
    load_watchlist,
    save_watchlist
)


def add_club_id(
        club_id
):

    club_id = str(
        club_id
    )

    watchlist = load_watchlist()

    if (
        club_id
        not in
        watchlist["club_ids"]
    ):

        watchlist[
            "club_ids"
        ].append(
            club_id
        )

        save_watchlist(
            watchlist
        )

        return True

    return False


def remove_club_id(
        club_id
):

    club_id = str(
        club_id
    )

    watchlist = load_watchlist()

    if (
        club_id
        in
        watchlist["club_ids"]
    ):

        watchlist[
            "club_ids"
        ].remove(
            club_id
        )

        save_watchlist(
            watchlist
        )

        return True

    return False