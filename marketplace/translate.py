from urllib.parse import parse_qsl, urlencode, urlparse

from config import LISTINGS_URL

RANGE_MAP = {
    "metadata.age": ("ageMin", "ageMax"),
    "metadata.overall": ("overallMin", "overallMax"),
    "listing.price": ("priceMin", "priceMax"),
    "metadata.pace": ("paceMin", "paceMax"),
    "metadata.shooting": ("shootingMin", "shootingMax"),
    "metadata.passing": ("passingMin", "passingMax"),
    "metadata.dribbling": ("dribblingMin", "dribblingMax"),
    "metadata.defense": ("defenseMin", "defenseMax"),
    "metadata.physical": ("physicalMin", "physicalMax"),
    "metadata.height": ("heightMin", "heightMax"),
}

RANGE_LABELS = {
    "metadata.age": "Age",
    "metadata.overall": "OVR",
    "listing.price": "Price",
    "metadata.pace": "Pac",
    "metadata.shooting": "Sho",
    "metadata.passing": "Pas",
    "metadata.dribbling": "Dri",
    "metadata.defense": "Def",
    "metadata.physical": "Phy",
}


def marketplace_type_from_path(pathname):
    p = (pathname or "").lower()
    if "/packs" in p:
        return "PACK"
    if "/clubs" in p:
        return "CLUB"
    return "PLAYER"


def page_url_to_api_url(page_url):
    try:
        url = urlparse(page_url)
        p = url.path.lower()
        api_params = {
            "limit": "25",
            "type": marketplace_type_from_path(p),
            "sorts": "listing.createdDateTime",
            "sortsOrders": "DESC",
            "status": "AVAILABLE",
            "view": "full",
        }
        for key, val in parse_qsl(url.query, keep_blank_values=True):
            if key == "sort":
                continue
            if key in RANGE_MAP:
                mn, mx = RANGE_MAP[key]
                parts = val.split(":")
                a = parts[0].strip() if parts else ""
                b = parts[1].strip() if len(parts) > 1 else ""
                if a:
                    api_params[mn] = a
                if b:
                    api_params[mx] = b
                continue
            if key in ("positions.name", "positions", "position"):
                api_params["positions"] = val
                continue
            if key == "activeContract" and "free" in val.lower():
                api_params["isFreeAgent"] = "true"
                continue
            if key not in ("page", "tab", "view", "type"):
                api_params[key] = val
        return f"{LISTINGS_URL}?{urlencode(api_params)}"
    except Exception:
        return None
