from healthcheck import (
    run_healthcheck
)


def health_command():

    report = run_healthcheck()

    lines = [

        f"Database: "

        f"{report['database']}",

        f"Wallet Cache: "

        f"{report['wallet_cache']}",

        f"Healthy: "

        f"{report['healthy']}"

    ]

    return "\n".join(
        lines
    )