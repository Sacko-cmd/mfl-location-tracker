def help_text():
    return """
**Getting started**
/register <webhook_url> — Link your Discord channel webhook to receive alerts
/unregister — Stop your alerts and remove your registration
/mysettings — Show your webhook and watchlist summary

**Watchlist (your alerts only)**
/add <city> — Watch a city for pool sales
/remove <city> — Stop watching a city
/watchall — Watch all cities
/list — Show your watchlist
/pause — Pause your notifications
/resume — Resume your notifications
/status — Summary counts of what you watch
/country <code> — Watch a country (e.g. ENG)
/country_remove <code> — Stop watching a country
/country_list — List countries you watch
/clubid <id> — Watch a specific club/location ID
/remove_clubid <id> — Stop watching a club ID
/club_list — List club IDs you watch

**Pool & search**
/wallet — How many locations are in the pool wallet right now
/search <query> — Find cities/countries/IDs in the pool wallet
/search <query> <limit> — Same, with custom result limit (max 50)
/club <id> — Look up who owns a club ID right now
/pending — Clubs that left the pool and are awaiting confirmation
/poollog — Recent pool departure events logged by the tracker

**History**
/recent — Last transfers recorded by the tracker
/recent <n> — Last n transfers (max 20)
/history <city> — Transfer history for a city
/manager <name> — Transfer history for a manager name
/export_history — Export transfer history to CSV on the server

**Tools**
/refresh — Force an immediate pool check now
/rebuild — Rebuild the MFL manager wallet cache
/stats — Tracker stats (managers cached, transfer count)
/health — Database and cache health check
/ping — Check if the bot is online
/help — Show this command list
/version — Show tracker version
"""


def help_setup_text():
    return """
**New user setup**
1. In Discord: channel → Integrations → Webhooks → New Webhook → copy URL
2. Run: `/register https://discord.com/api/webhooks/...`
3. Run: `/watchall` or `/add Nashville` to choose what to watch
4. Alerts go to your channel only — your list does not affect other users
"""
