import csv
import sqlite3

from config import (
    DATABASE_FILE
)


EXPORT_FILE = (
    "transfers.csv"
)


def export_history_csv():

    conn = sqlite3.connect(
        DATABASE_FILE
    )

    cursor = conn.cursor()

    cursor.execute(

        """

        SELECT *

        FROM transfers

        ORDER BY timestamp DESC

        """

    )

    rows = cursor.fetchall()

    conn.close()

    with open(

        EXPORT_FILE,

        "w",

        newline="",

        encoding="utf8"

    ) as f:

        writer = csv.writer(
            f
        )

        writer.writerow(

            [

                "id",

                "timestamp",

                "club_id",

                "city",

                "country",

                "manager",

                "wallet",

                "club_name"

            ]

        )

        writer.writerows(
            rows
        )

    return EXPORT_FILE