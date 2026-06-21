from database import (
    get_subscriber,
    is_registered,
    list_subscribers,
    register_subscriber,
    unregister_subscriber,
)
from watchlist import ensure_watchlist


def is_valid_webhook_url(url):
    return url.startswith("https://discord.com/api/webhooks/")


def register_user(discord_user_id, webhook_url):
    if not is_valid_webhook_url(webhook_url):
        raise ValueError("Webhook must start with https://discord.com/api/webhooks/")

    register_subscriber(discord_user_id, webhook_url.strip())
    ensure_watchlist(discord_user_id)
    return True


def unregister_user(discord_user_id):
    unregister_subscriber(discord_user_id)
    return True


def get_user_settings(discord_user_id):
    subscriber = get_subscriber(discord_user_id)
    if not subscriber:
        return None

    from watchlist import load_watchlist

    watchlist = load_watchlist(discord_user_id)
    webhook = subscriber["webhook_url"]
    masked = webhook[:40] + "..." if len(webhook) > 40 else webhook
    return {
        "registered": True,
        "webhook_preview": masked,
        "created_at": subscriber["created_at"],
        **watchlist,
    }


def get_notification_targets():
    return list_subscribers()
