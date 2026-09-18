import json

from config import data_file

CACHE_FILE = data_file("recipient_cache.json")


def load_recipient_cache():

    try:

        with open(

            CACHE_FILE,

            encoding="utf8"

        ) as f:

            return json.load(f)

    except FileNotFoundError:

        return {}


def save_recipient_cache(

        data

):

    with open(

        CACHE_FILE,

        "w",

        encoding="utf8"

    ) as f:

        json.dump(

            data,

            f,

            indent=2

        )