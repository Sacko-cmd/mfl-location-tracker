def build_embed(
    city,
    country,
    manager,
    wallet,
    club_name,
    club_id,
):
    return {
        "title": "🚨 NEW LOCATION CLAIMED",
        "color": 0x00FF00,
        "fields": [
            {"name": "City", "value": city or "Unknown", "inline": False},
            {"name": "Country", "value": country or "Unknown", "inline": False},
            {"name": "Manager", "value": manager, "inline": False},
            {"name": "Wallet", "value": wallet, "inline": False},
            {"name": "Club", "value": club_name, "inline": False},
            {"name": "Club ID", "value": str(club_id), "inline": False},
        ],
    }
