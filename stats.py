import json
import sqlite3

from config import (
    DATABASE_FILE,
    WALLET_CACHE_FILE
)


LAST_REFRESH_FILE = (
    "last_refresh.json"
)


def get_manager_count():

    try:

        with open(
            WALLET_CACHE_FILE,
            encoding="utf8"
        ) as f:

            wallets = json.load(f)

        return len(
            wallets
        )

    except Exception:

        return 0


def get_transfer_count():

    conn = sqlite3.connect(
        DATABASE_FILE
    )

    cursor = conn.cursor()

    cursor.execute(

        """

        SELECT COUNT(*)

        FROM transfers

        """

    )

    count = cursor.fetchone()[0]

    conn.close()

    return count


def get_last_refresh():

    try:

        with open(
            LAST_REFRESH_FILE,
            encoding="utf8"
        ) as f:

            data = json.load(f)

        return data[
            "last_refresh"
        ]

    except Exception:

        return "Never"


def get_stats():

    return {

        "manager_count":

        get_manager_count(),

        "transfer_count":

        get_transfer_count(),

        "last_refresh":

        get_last_refresh()

    }