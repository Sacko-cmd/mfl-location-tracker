from club_lookup import fetch_wallet_clubs


def find_recipient(
        city,
        wallet_cache
):

    for wallet, manager in wallet_cache.items():

        try:

            clubs = fetch_wallet_clubs(wallet)

            for item in clubs:

                club = item["club"]

                if club["city"] == city:

                    return {

                        "manager": manager,

                        "wallet": wallet,

                        "club_name": club["name"],

                        "club_id": club["id"]
                    }

        except Exception:

            continue

    return None