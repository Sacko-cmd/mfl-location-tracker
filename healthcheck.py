import json
import sqlite3

from config import (
    DATABASE_FILE,
    WALLET_CACHE_FILE
)


def run_healthcheck():

    report = {

        "database": False,

        "wallet_cache": False

    }

    try:

        conn = sqlite3.connect(
            DATABASE_FILE
        )

        conn.close()

        report[
            "database"
        ] = True

    except Exception:

        pass

    try:

        with open(
            WALLET_CACHE_FILE,
            encoding="utf8"
        ) as f:

            json.load(f)

        report[
            "wallet_cache"
        ] = True

    except Exception:

        pass

    report[
        "healthy"
    ] = all(
        report.values()
    )

    return report