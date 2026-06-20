import requests

from config import LEADERBOARD_URL


LIMIT = 20


def get_all_managers():

    offset = 0

    managers = []

    while True:

        response = requests.get(
            LEADERBOARD_URL,
            params={
                "sort": "nbMflPoints",
                "sortOrder": "DESC",
                "limit": LIMIT,
                "offset": offset
            }
        )

        response.raise_for_status()

        data = response.json()

        users = data["users"]

        managers.extend(users)

        print(
            f"Loaded offset {offset} "
            f"({len(users)} users)"
        )

        if len(users) < LIMIT:
            break

        offset += LIMIT

    return managers