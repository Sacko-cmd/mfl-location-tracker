from datetime import datetime


def utc_now():

    return datetime.utcnow()


def utc_now_iso():

    return (

        datetime.utcnow()

        .isoformat()

    )


def safe_upper(
        value
):

    if value is None:

        return ""

    return str(
        value
    ).upper()


def normalise_city(
        city
):

    if city is None:

        return ""

    return (

        str(city)

        .strip()

        .lower()

    )