from datetime import datetime


def log_info(
        message
):

    print(

        f"[INFO] "

        f"{datetime.utcnow()} "

        f"{message}"

    )


def log_warning(
        message
):

    print(

        f"[WARNING] "

        f"{datetime.utcnow()} "

        f"{message}"

    )


def log_error(
        message
):

    print(

        f"[ERROR] "

        f"{datetime.utcnow()} "

        f"{message}"

    )