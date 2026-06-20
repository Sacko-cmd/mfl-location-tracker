from flowty import fetch_locations


def search_locations(query):
    query = query.strip()
    if not query:
        return []

    locations = fetch_locations()
    query_lower = query.lower()
    matches = []

    for location in locations.values():
        city = location.get("city") or ""
        country = location.get("country") or ""
        club_id = str(location.get("club_id") or "")

        if (
            query_lower in city.lower()
            or query_lower in country.lower()
            or query == club_id
        ):
            matches.append(location)

    matches.sort(key=lambda item: (item.get("city") or "", item.get("club_id") or ""))
    return matches
