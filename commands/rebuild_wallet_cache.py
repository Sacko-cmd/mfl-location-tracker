from wallet_refresh import (
    run_wallet_refresh
)


def rebuild_wallet_cache():

    run_wallet_refresh()

    return (

        "Wallet cache "

        "successfully rebuilt."

    )