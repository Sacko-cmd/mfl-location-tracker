from recipient_cache import (

    load_recipient_cache,

    save_recipient_cache

)


MAX_SIZE = 10000


def cleanup_cache():

    cache = (

        load_recipient_cache()

    )

    keys = list(

        cache.keys()

    )

    if len(keys) <= MAX_SIZE:

        return

    trimmed = {

        k: cache[k]

        for k in

        keys[-MAX_SIZE:]

    }

    save_recipient_cache(

        trimmed

    )