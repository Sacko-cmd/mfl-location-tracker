import time
from datetime import datetime, timezone

import requests

from config import REQUEST_TIMEOUT_SECONDS
from logger import log_error, log_info
from marketplace.extract import (
    build_alert_text,
    extract_meta,
    format_price,
    get_item_url,
    get_listing_id,
)
from marketplace.storage import load_monitors, save_monitors


def send_discord(monitor, items):
    webhook = monitor.get("discordWebhook")
    if not webhook:
        return

    for i, item in enumerate(items):
        meta = extract_meta(item, monitor)
        item_url = get_item_url(item, monitor)
        fields = [{"name": "Filter", "value": monitor.get("label") or "monitor", "inline": False}]

        if meta["listingType"] == "CLUB":
            fields.extend([
                {"name": "Club", "value": meta["clubName"], "inline": True},
                {"name": "Location", "value": meta["location"], "inline": True},
                {"name": "Price", "value": format_price(meta["price"]), "inline": True},
            ])
            if meta.get("owner"):
                fields.append({"name": "Owner", "value": meta["owner"], "inline": True})
        elif meta["listingType"] == "PACK":
            fields.extend([
                {"name": "Pack", "value": meta["packName"], "inline": True},
                {"name": "Price", "value": format_price(meta["price"]), "inline": True},
            ])
            if meta.get("packType"):
                fields.append({"name": "Type", "value": meta["packType"], "inline": True})
            if meta.get("owner"):
                fields.append({"name": "Owner", "value": meta["owner"], "inline": True})
        else:
            fields.extend([
                {"name": "Player", "value": meta["name"], "inline": True},
                {"name": "Price", "value": format_price(meta["price"]), "inline": True},
            ])
            if meta.get("stats"):
                fields.append({"name": "Stats", "value": meta["stats"], "inline": False})
            if meta.get("owner"):
                fields.append({"name": "Owner", "value": meta["owner"], "inline": True})

        kind = "club" if meta["listingType"] == "CLUB" else "pack" if meta["listingType"] == "PACK" else "player"
        fields.append({
            "name": "Open",
            "value": f"[View {kind}]({item_url})",
            "inline": False,
        })

        color = 0xF58426 if meta["listingType"] == "CLUB" else 0x9B59B6 if meta["listingType"] == "PACK" else 0x2563EB
        payload = {
            "username": "MFL Monitor",
            "content": build_alert_text(item, monitor),
            "embeds": [{
                "title": meta["name"],
                "url": item_url,
                "description": build_alert_text(item, monitor),
                "color": color,
                "fields": fields,
                "footer": {"text": "MFL Monitor"},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }],
        }

        try:
            r = requests.post(webhook, json=payload, timeout=REQUEST_TIMEOUT_SECONDS)
            if not r.ok:
                log_error(f"[Discord] HTTP {r.status_code} for \"{monitor.get('label')}\"")
        except Exception as e:
            log_error(f"[Discord] Error for \"{monitor.get('label')}\": {e}")

        if i < len(items) - 1:
            time.sleep(0.5)


def poll_monitor(monitor):
    if not monitor.get("apiUrl") or not monitor.get("enabled"):
        return

    label = monitor.get("label") or monitor.get("id")
    log_info(f"[Marketplace] Polling: {label}")

    try:
        r = requests.get(monitor["apiUrl"], timeout=REQUEST_TIMEOUT_SECONDS)
        r.raise_for_status()
        json_data = r.json()
        if isinstance(json_data, list):
            listings = json_data
        else:
            listings = json_data.get("listings") or json_data.get("data") or json_data.get("results") or []

        monitors = load_monitors()
        idx = next((i for i, m in enumerate(monitors) if m.get("id") == monitor.get("id")), -1)
        if idx == -1:
            return

        seen_ids = monitors[idx].get("seenIds") or []
        new_items = [
            item for item in listings
            if get_listing_id(item) and get_listing_id(item) not in seen_ids
        ]

        all_ids = [get_listing_id(item) for item in listings if get_listing_id(item)]
        merged = list(dict.fromkeys(seen_ids + all_ids))[-500:]
        monitors[idx]["seenIds"] = merged
        monitors[idx]["lastCheck"] = datetime.now(timezone.utc).isoformat()
        monitors[idx]["lastError"] = None
        if new_items:
            monitors[idx]["newCount"] = (monitors[idx].get("newCount") or 0) + len(new_items)
        save_monitors(monitors)

        if not new_items:
            log_info(f"[Marketplace] {label}: no new listings")
            return

        log_info(f"[Marketplace] {label}: {len(new_items)} new — sending to Discord")
        if monitor.get("discordWebhook"):
            send_discord(monitor, new_items)

    except Exception as e:
        log_error(f"[Marketplace] {label}: {e}")
        monitors = load_monitors()
        idx = next((i for i, m in enumerate(monitors) if m.get("id") == monitor.get("id")), -1)
        if idx != -1:
            monitors[idx]["lastError"] = str(e)
            save_monitors(monitors)
