from config import LEADERBOARD_URL
from logger import log_info
from mfl_api import mfl_get

LIMIT = 20


def get_all_managers():
    offset = 0
    managers = []

    log_info("Starting MFL leaderboard scan...")

    while True:
        log_info(f"Fetching leaderboard offset {offset}...")
        response = mfl_get(
            LEADERBOARD_URL,
            params={
                "sort": "nbMflPoints",
                "sortOrder": "DESC",
                "limit": LIMIT,
                "offset": offset,
            },
        )
        response.raise_for_status()

        data = response.json()
        users = data["users"]
        managers.extend(users)

        log_info(f"Loaded offset {offset} ({len(users)} users, {len(managers)} total)")

        if len(users) < LIMIT:
            break

        offset += LIMIT

    log_info(f"Leaderboard scan complete: {len(managers)} managers.")
    return managers
