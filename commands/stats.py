from stats import (
    get_stats
)


def stats_command():

    stats = get_stats()

    lines = [

        f"Managers cached: "

        f"{stats['manager_count']}",

        f"Transfers tracked: "

        f"{stats['transfer_count']}",

        f"Last wallet refresh: "

        f"{stats['last_refresh']}"

    ]

    return "\n".join(
        lines
    )