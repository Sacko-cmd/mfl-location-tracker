from history import (
    get_city_history
)


def history_command(
        city
):

    rows = get_city_history(
        city
    )

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