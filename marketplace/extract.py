def get_listing_id(item):
    raw = (
        item.get("listingResourceId")
        or item.get("id")
        or item.get("listingId")
        or item.get("_id")
    )
    if raw is None:
        return None
    return str(raw)


def get_listing_type(item, monitor):
    if item.get("club"):
        return "CLUB"
    if item.get("pack"):
        return "PACK"
    if item.get("player"):
        return "PLAYER"
    page_url = (monitor.get("pageUrl") or "").lower()
    api_url = (monitor.get("apiUrl") or "").lower()
    if "/packs" in page_url or "type=pack" in api_url:
        return "PACK"
    if "/clubs" in page_url or "type=club" in api_url:
        return "CLUB"
    return "PLAYER"


def format_location(city, country):
    parts = [v.strip() for v in (city, country) if v and str(v).strip()]
    return ", ".join(parts) or "Unknown location"


def format_owner(item):
    return (
        item.get("sellerName")
        or (item.get("club") or {}).get("ownedBy", {}).get("name")
        or (item.get("player") or {}).get("ownedBy", {}).get("name")
        or (item.get("pack") or {}).get("ownedBy", {}).get("name")
        or ""
    )


def format_stats(meta):
    parts = []
    if meta.get("overall") is not None:
        parts.append(f"OVR {meta['overall']}")
    if meta.get("posStr"):
        parts.append(meta["posStr"])
    if meta.get("age") is not None:
        parts.append(f"Age {meta['age']}")
    attrs = [
        f"PAC {meta['pace']}" if meta.get("pace") is not None else None,
        f"SHO {meta['shooting']}" if meta.get("shooting") is not None else None,
        f"PAS {meta['passing']}" if meta.get("passing") is not None else None,
        f"DRI {meta['dribbling']}" if meta.get("dribbling") is not None else None,
        f"DEF {meta['defense']}" if meta.get("defense") is not None else None,
        f"PHY {meta['physical']}" if meta.get("physical") is not None else None,
    ]
    attrs = [a for a in attrs if a]
    if attrs:
        parts.append(" · ".join(attrs))
    return " · ".join(parts)


def extract_meta(item, monitor):
    listing_type = get_listing_type(item, monitor)
    price = item.get("price")
    if price is None:
        price = (item.get("listing") or {}).get("price")
    owner = format_owner(item)

    if listing_type == "CLUB":
        club = item.get("club") or {}
        club_name = (club.get("name") or "").strip() or f"Club #{club.get('id', '?')}"
        location = format_location(club.get("city"), club.get("country"))
        return {
            "listingType": "CLUB",
            "name": club_name,
            "clubName": club_name,
            "location": location,
            "price": price,
            "owner": owner,
            "stats": "",
        }

    if listing_type == "PACK":
        pack = item.get("pack") or {}
        template = pack.get("packTemplate") or {}
        pack_name = (template.get("name") or template.get("type") or "Pack").strip()
        return {
            "listingType": "PACK",
            "name": pack_name,
            "packName": pack_name,
            "packType": template.get("type") or "",
            "price": price,
            "owner": owner,
            "stats": "",
        }

    player = item.get("player") or {}
    meta = player.get("metadata") or {}
    first = meta.get("firstName") or player.get("firstName") or ""
    last = meta.get("lastName") or player.get("lastName") or ""
    if first and last:
        name = f"{first} {last}"
    else:
        name = last or first or "Unknown player"
    extracted = {
        "listingType": "PLAYER",
        "name": name,
        "price": price,
        "owner": owner,
        "overall": meta.get("overall", player.get("overall")),
        "posStr": "/".join((meta.get("positions") or player.get("positions") or [])[:2]),
        "age": meta.get("age"),
        "pace": meta.get("pace"),
        "shooting": meta.get("shooting"),
        "passing": meta.get("passing"),
        "dribbling": meta.get("dribbling"),
        "defense": meta.get("defense"),
        "physical": meta.get("physical"),
    }
    extracted["stats"] = format_stats(extracted)
    return extracted


def get_item_url(item, monitor):
    listing_type = get_listing_type(item, monitor)

    if listing_type == "CLUB":
        club = item.get("club") or {}
        if club.get("id"):
            return f"https://app.playmfl.com/clubs/{club['id']}"
        return "https://app.playmfl.com/marketplace/clubs"

    if listing_type == "PACK":
        listing_id = get_listing_id(item)
        if listing_id:
            return f"https://app.playmfl.com/marketplace/packs?listingResourceId={listing_id}"
        chain_id = (item.get("pack") or {}).get("chainId")
        if chain_id:
            return f"https://app.playmfl.com/marketplace/packs?chainId={chain_id}"
        return "https://app.playmfl.com/marketplace/packs"

    player = item.get("player") or {}
    meta = player.get("metadata") or {}
    slug = (
        player.get("slug")
        or meta.get("slug")
        or player.get("playerSlug")
        or meta.get("playerSlug")
    )
    player_id = (
        player.get("id")
        or player.get("playerId")
        or meta.get("id")
        or meta.get("playerId")
        or item.get("playerId")
    )
    if slug:
        return f"https://app.playmfl.com/players/{slug}"
    if player_id:
        return f"https://app.playmfl.com/players/{player_id}"
    return "https://app.playmfl.com/marketplace/players"


def format_price(price):
    if price is not None:
        return f"${price}"
    return "Price N/A"


def build_alert_text(item, monitor):
    meta = extract_meta(item, monitor)
    label = monitor.get("label") or "monitor"
    if meta["listingType"] == "CLUB":
        return f"{label} · {meta['clubName']} · {meta['location']} · {format_price(meta['price'])}"
    if meta["listingType"] == "PACK":
        return f"{label} · {meta['packName']} · {format_price(meta['price'])}"
    stats = meta.get("stats") or "Player"
    return f"{label} · {meta['name']} · {stats} · {format_price(meta['price'])}"
