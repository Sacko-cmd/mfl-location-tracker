from datetime import datetime

from database import insert_transfer
from discord_notifications import send_notification
from flowty import fetch_locations
from logger import log_info, log_warning
from recipient_lookup import find_recipient
from rich_embed import build_embed
from storage import load_state, save_state
from wallet_cache import load_wallet_cache
from watchlist import should_notify


def detect_transfers():
    previous = load_state()
    current = fetch_locations()

    disappeared = set(previous.keys()) - set(current.keys())
    events = []
    processed = set()

    if not disappeared:
        save_state(current)
        return events

    wallet_cache = load_wallet_cache()
    if not wallet_cache:
        log_warning(
            "Wallet cache is empty; keeping previous state so departures can be retried."
        )
        return events

    for club_id in disappeared:
        club = previous[club_id]
        city = club["city"]
        country = club["country"]

        if not should_notify(city, country, club_id):
            processed.add(club_id)
            continue

        recipient = find_recipient(city, wallet_cache)
        if recipient is None:
            log_warning(
                f"No recipient found for {city}, {country} (club {club_id}). Will retry."
            )
            continue

        processed.add(club_id)

        insert_transfer(
            timestamp=datetime.utcnow().isoformat(),
            club_id=club_id,
            city=city,
            country=country,
            manager=recipient["manager"],
            wallet=recipient["wallet"],
            club_name=recipient["club_name"],
        )

        event = {
            "club_id": club_id,
            "city": city,
            "country": country,
            **recipient,
        }
        events.append(event)

        try:
            embed = build_embed(
                city=city,
                country=country,
                manager=recipient["manager"],
                wallet=recipient["wallet"],
                club_name=recipient["club_name"],
                club_id=club_id,
            )
            send_notification(embed)
            log_info(f"Sent notification for {city}, {country}.")
        except Exception as e:
            log_warning(f"Failed to send notification for {city}: {e}")

    new_state = dict(current)
    for club_id in disappeared:
        if club_id not in processed:
            new_state[club_id] = previous[club_id]

    save_state(new_state)
    return events
