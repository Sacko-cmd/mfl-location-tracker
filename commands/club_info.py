from club_lookup import fetch_club_by_id


def club_info(club_id):
    club = fetch_club_by_id(club_id)
    owned_by = club.get("ownedBy") or {}
    return {
        "club_id": str(club.get("id") or club_id),
        "city": club.get("city"),
        "country": club.get("country"),
        "club_name": club.get("name") or "",
        "manager": owned_by.get("name") or "Unknown",
        "wallet": owned_by.get("walletAddress") or "Unknown",
        "status": club.get("status"),
    }
