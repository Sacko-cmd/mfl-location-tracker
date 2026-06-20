import json


STATE_FILE = "ownership.json"


def save_state(data):

    with open(
        STATE_FILE,
        "w",
        encoding="utf8"
    ) as f:

        json.dump(
            data,
            f,
            indent=2
        )


def load_state():

    try:

        with open(
            STATE_FILE,
            encoding="utf8"
        ) as f:

            return json.load(f)

    except FileNotFoundError:

        return {}