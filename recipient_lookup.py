from club_lookup import fetch_club_by_id
from config import CENTRAL_WALLET
from logger import log_warning


def find_recipient(club_id):
    try:
        club = fetch_club_by_id(club_id)
    except Exception as e:
        log_warning(f"Club lookup failed for ID {club_id}: {e}")
        return None

    owned_by = club.get("ownedBy") or {}
    wallet = owned_by.get("walletAddress")
    if not wallet:
        return None

    if wallet.lower() == CENTRAL_WALLET.lower():
        return None

    return {
        "manager": owned_by.get("name") or "Unknown",
        "wallet": wallet,
        "club_name": club.get("name") or "",
        "club_id": str(club.get("id") or club_id),
        "city": club.get("city"),
        "country": club.get("country"),
    }
