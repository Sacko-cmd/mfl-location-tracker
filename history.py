import sqlite3

from config import (
    DATABASE_FILE
)


def get_city_history(
        city
):

    conn = sqlite3.connect(
        DATABASE_FILE
    )

    cursor = conn.cursor()

    cursor.execute(

        """

        SELECT *

        FROM transfers

        WHERE city=?

        ORDER BY timestamp DESC

        """,

        (city,)

    )

    rows = cursor.fetchall()

    conn.close()

    return rows


def get_recent_history(limit=10):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT *
        FROM transfers
        ORDER BY timestamp DESC
        LIMIT ?
        """,
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_manager_history(
        manager
):

    conn = sqlite3.connect(
        DATABASE_FILE
    )

    cursor = conn.cursor()

    cursor.execute(

        """

        SELECT *

        FROM transfers

        WHERE manager=?

        ORDER BY timestamp DESC

        """,

        (manager,)

    )

    rows = cursor.fetchall()

    conn.close()

    return rows