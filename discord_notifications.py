import requests

from config import DISCORD_WEBHOOK_URL
from logger import log_info, log_warning


def send_notification(embed):
    if not DISCORD_WEBHOOK_URL:
        log_warning("DISCORD_WEBHOOK_URL not set; skipping notification.")
        return

    payload = {
        "embeds": [embed],
    }

    response = requests.post(
        DISCORD_WEBHOOK_URL,
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    log_info("Discord webhook notification sent.")
