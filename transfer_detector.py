from datetime import datetime

from club_lookup import fetch_club_by_id
from config import (
    CENTRAL_WALLET,
    CONFIRM_MISSING_POLLS,
    MAX_DEPARTURE_AGE_HOURS,
)
from database import insert_transfer
from discord_notifications import send_notification
from flowty import fetch_locations
from logger import log_info, log_warning
from pool_log import log_pool_event
from recipient_lookup import find_recipient, is_owned_by_pool
from rich_embed import build_embed
from storage import build_pool_entry, load_state, save_state
from watchlist import should_notify


def _hours_since(iso_timestamp):
    seen = datetime.fromisoformat(iso_timestamp)
    return (datetime.utcnow() - seen).total_seconds() / 3600


def _notify_subscribers(city, country, club_id, embed):
    from config import DISCORD_WEBHOOK_URL
    from subscribers import get_notification_targets

    sent = 0
    for sub in get_notification_targets():
        user_id = sub["discord_user_id"]
        if not should_notify(user_id, city, country, club_id):
            continue
        try:
            send_notification(embed, webhook_url=sub["webhook_url"])
            sent += 1
            log_info(f"Notified subscriber {user_id} for club {club_id}.")
        except Exception as e:
            log_warning(f"Failed to notify subscriber {user_id}: {e}")

    if DISCORD_WEBHOOK_URL:
        try:
            send_notification(embed, webhook_url=DISCORD_WEBHOOK_URL)
            sent += 1
        except Exception as e:
            log_warning(f"Failed to notify admin webhook: {e}")

    if sent == 0:
        log_warning(f"No subscribers notified for club {club_id}.")


def detect_transfers():
    previous = load_state()
    current = fetch_locations()

    disappeared = set(previous.keys()) - set(current.keys())
    events = []
    processed = set()
    new_state = {
        club_id: build_pool_entry(club)
        for club_id, club in current.items()
    }

    if not disappeared:
        save_state(new_state)
        return events

    for club_id in disappeared:
        prev = previous[club_id]
        city = prev.get("city")
        country = prev.get("country")

        missing_since = prev.get("missing_since") or datetime.utcnow().isoformat()
        missing_polls = (prev.get("missing_polls") or 0) + 1

        ghost = {
            **build_pool_entry(prev),
            "missing_since": missing_since,
            "missing_polls": missing_polls,
        }

        log_pool_event(
            {
                "club_id": club_id,
                "city": city,
                "country": country,
                "status": "missing",
                "missing_polls": missing_polls,
            }
        )

        if missing_polls < CONFIRM_MISSING_POLLS:
            log_info(
                f"Club {club_id} missing from pool "
                f"({missing_polls}/{CONFIRM_MISSING_POLLS} checks). Waiting to confirm."
            )
            new_state[club_id] = ghost
            continue

        age_hours = _hours_since(missing_since)
        if age_hours > MAX_DEPARTURE_AGE_HOURS:
            log_warning(
                f"Club {club_id} missing for {age_hours:.1f}h without alert. "
                f"Dropping stale entry without notifying."
            )
            log_pool_event(
                {
                    "club_id": club_id,
                    "city": city,
                    "country": country,
                    "status": "stale_dropped",
                }
            )
            processed.add(club_id)
            continue

        if club_id in current:
            log_info(f"Club {club_id} reappeared in pool. Ignoring false departure.")
            processed.add(club_id)
            continue

        if is_owned_by_pool(club_id):
            log_info(
                f"Club {club_id} still owned by pool wallet. Waiting for ownership update."
            )
            new_state[club_id] = ghost
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
            new_state[club_id] = ghost
            continue

        if str(recipient["club_id"]) != str(club_id):
            log_warning(
                f"Club ID mismatch for {club_id}: API returned {recipient['club_id']}. Skipping."
            )
            new_state[club_id] = ghost
            continue

        processed.add(club_id)
        city = recipient.get("city") or city
        country = recipient.get("country") or country

        insert_transfer(
            timestamp=datetime.utcnow().isoformat(),
            club_id=str(club_id),
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

        events.append(
            {
                "club_id": str(club_id),
                "city": city,
                "country": country,
                **recipient,
            }
        )

        try:
            embed = build_embed(
                city=city,
                country=country,
                manager=recipient["manager"],
                wallet=recipient["wallet"],
                club_name=recipient["club_name"],
                club_id=str(club_id),
            )
            _notify_subscribers(city, country, club_id, embed)
            log_info(f"Processed notification for {city}, {country} (club {club_id}).")
        except Exception as e:
            log_warning(f"Failed to send notification for club {club_id}: {e}")

    for club_id in disappeared:
        if club_id not in processed and club_id not in new_state:
            new_state[club_id] = {
                **build_pool_entry(previous[club_id]),
                "missing_since": previous[club_id].get("missing_since")
                or datetime.utcnow().isoformat(),
                "missing_polls": previous[club_id].get("missing_polls") or 0,
            }

    save_state(new_state)
    return events
