import requests

from config import LEADERBOARD_URL, REQUEST_TIMEOUT_SECONDS
from logger import log_info

LIMIT = 20


def get_all_managers():
    offset = 0
    managers = []

    log_info("Starting MFL leaderboard scan...")

    while True:
        log_info(f"Fetching leaderboard offset {offset}...")
        response = requests.get(
            LEADERBOARD_URL,
            params={
                "sort": "nbMflPoints",
                "sortOrder": "DESC",
                "limit": LIMIT,
                "offset": offset,
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
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
