from datetime import datetime

from database import insert_transfer
from discord_notifications import send_notification
from flowty import fetch_locations
from logger import log_info, log_warning
from pool_log import log_pool_event
from recipient_lookup import find_recipient
from rich_embed import build_embed
from storage import load_state, save_state
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

    for club_id in disappeared:
        club = previous[club_id]
        city = club.get("city")
        country = club.get("country")

        log_pool_event(
            {
                "club_id": club_id,
                "city": city,
                "country": country,
                "status": "departed",
            }
        )

        if not should_notify(city, country, club_id):
            processed.add(club_id)
            continue

        recipient = find_recipient(club_id)
        if recipient is None:
            log_warning(
                f"No owner found yet for club {club_id} ({city}, {country}). Will retry."
            )
            log_pool_event(
                {
                    "club_id": club_id,
                    "city": city,
                    "country": country,
                    "status": "unmatched",
                }
            )
            continue

        processed.add(club_id)
        city = recipient.get("city") or city
        country = recipient.get("country") or country

        insert_transfer(
            timestamp=datetime.utcnow().isoformat(),
            club_id=club_id,
            city=city,
            country=country,
            manager=recipient["manager"],
            wallet=recipient["wallet"],
            club_name=recipient["club_name"],
        )

        log_pool_event(
            {
                "club_id": club_id,
                "city": city,
                "country": country,
                "status": "matched",
                "manager": recipient["manager"],
                "wallet": recipient["wallet"],
            }
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
            log_info(f"Sent notification for {city}, {country} (club {club_id}).")
        except Exception as e:
            log_warning(f"Failed to send notification for club {club_id}: {e}")

    new_state = dict(current)
    for club_id in disappeared:
        if club_id not in processed:
            new_state[club_id] = previous[club_id]

    save_state(new_state)
    return events
