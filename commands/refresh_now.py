from main import (
    check_transfers
)


def refresh_now():

    try:

        check_transfers()

        return (

            "Transfer check "

            "completed."

        )

    except Exception as e:

        return (

            f"Refresh failed: "

            f"{e}"

        )