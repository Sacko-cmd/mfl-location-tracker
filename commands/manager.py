import sqlite3

from config import (
    DATABASE_FILE
)


def manager_history(
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

    output = []

    for row in rows:

        output.append(

            {

                "timestamp":

                row[1],

                "club_id":

                row[2],

                "city":

                row[3],

                "country":

                row[4],

                "manager":

                row[5],

                "wallet":

                row[6],

                "club_name":

                row[7]

            }

        )

    return output