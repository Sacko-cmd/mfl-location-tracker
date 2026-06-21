import json

from database import _connect

DEFAULT_WATCHLIST = {
    "cities": ["*"],
    "countries": [],
    "club_ids": [],
    "paused": False,
}


def create_watchlist():
    pass


def _default_row(user_id):
    return (
        str(user_id),
        json.dumps(DEFAULT_WATCHLIST["cities"]),
        json.dumps(DEFAULT_WATCHLIST["countries"]),
        json.dumps(DEFAULT_WATCHLIST["club_ids"]),
        0,
    )


def ensure_watchlist(user_id):
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT discord_user_id FROM user_watchlists WHERE discord_user_id=?",
        (str(user_id),),
    )
    if cursor.fetchone() is None:
        cursor.execute(
            """
            INSERT INTO user_watchlists(
                discord_user_id, cities, countries, club_ids, paused
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            _default_row(user_id),
        )
        conn.commit()
    conn.close()


def load_watchlist(user_id):
    from database import is_registered

    if not is_registered(user_id):
        return dict(DEFAULT_WATCHLIST)

    ensure_watchlist(user_id)
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT cities, countries, club_ids, paused
        FROM user_watchlists
        WHERE discord_user_id=?
        """,
        (str(user_id),),
    )
    row = cursor.fetchone()
    conn.close()
    return {
        "cities": json.loads(row[0]),
        "countries": json.loads(row[1]),
        "club_ids": json.loads(row[2]),
        "paused": bool(row[3]),
    }


def save_watchlist(user_id, data):
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO user_watchlists(
            discord_user_id, cities, countries, club_ids, paused
        )
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(discord_user_id) DO UPDATE SET
            cities=excluded.cities,
            countries=excluded.countries,
            club_ids=excluded.club_ids,
            paused=excluded.paused
        """,
        (
            str(user_id),
            json.dumps(data["cities"]),
            json.dumps(data["countries"]),
            json.dumps(data["club_ids"]),
            1 if data["paused"] else 0,
        ),
    )
    conn.commit()
    conn.close()


def should_notify(user_id, city, country, club_id):
    watchlist = load_watchlist(user_id)

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
