import requests

from config import DISCORD_WEBHOOK_URL
from logger import log_info, log_warning


def send_notification(embed, webhook_url=None):
    url = webhook_url or DISCORD_WEBHOOK_URL
    if not url:
        log_warning("No webhook URL provided; skipping notification.")
        return

    payload = {
        "embeds": [embed],
    }

    response = requests.post(
        url,
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    log_info("Discord webhook notification sent.")
