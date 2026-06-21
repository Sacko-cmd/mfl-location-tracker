import time

import discord
from discord.ext import commands

from config import DISCORD_TOKEN
from commands.add import add_city
from commands.club_info import club_info
from commands.club_list import get_club_list
from commands.clubid import add_club_id, remove_club_id
from commands.country import add_country, remove_country
from commands.country_list import get_country_list
from commands.export_history import export_history
from commands.health import health_command
from commands.help import help_setup_text, help_text
from commands.history import history_command, recent_command
from commands.list import list_watchlist
from commands.manager import manager_history
from commands.pause import pause_notifications, resume_notifications
from commands.pool_status import get_pending_departures
from commands.rebuild_wallet_cache import rebuild_wallet_cache
from commands.refresh_now import refresh_now
from commands.remove import remove_city
from commands.search import search_locations
from commands.stats import stats_command
from commands.status import get_status
from commands.version import version
from commands.watchall import enable_watchall
from database import is_registered
from flowty import fetch_locations
from logger import log_error, log_info
from pool_log import read_pool_log
from subscribers import get_user_settings, register_user, unregister_user

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents, help_command=None)


def uid(ctx):
    return str(ctx.author.id)


async def ensure_registered(ctx):
    if not is_registered(uid(ctx)):
        await ctx.send(
            "You are not registered yet.\n"
            "Run `/register <webhook_url>` first, or `/help setup` for steps."
        )
        return False
    return True


@bot.event
async def on_ready():
    log_info(f"Discord bot logged in as {bot.user} (ID {bot.user.id})")


@bot.event
async def on_disconnect():
    log_error("Discord bot disconnected from gateway.")


@bot.event
async def on_resumed():
    log_info("Discord bot connection resumed.")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing argument. Try `/help` for usage.")
        return

    if isinstance(error, commands.CommandNotFound):
        return

    log_error(f"Discord command error: {error}")
    await ctx.send(f"Command failed: {error}")


@bot.command(name="help")
async def help_cmd(ctx, topic: str = ""):
    if topic.lower() == "setup":
        await ctx.send(help_setup_text())
        return
    await ctx.send(help_text())


@bot.command(name="register")
async def register_cmd(ctx, *, webhook_url: str):
    try:
        register_user(uid(ctx), webhook_url.strip())
        await ctx.send(
            "Registered successfully. Alerts will go to your webhook.\n"
            "Next: `/watchall` or `/add <city>` to choose what to watch."
        )
    except ValueError as e:
        await ctx.send(str(e))


@bot.command(name="unregister")
async def unregister_cmd(ctx):
    unregister_user(uid(ctx))
    await ctx.send("Unregistered. You will no longer receive alerts.")


@bot.command(name="mysettings")
async def mysettings(ctx):
    settings = get_user_settings(uid(ctx))
    if not settings:
        await ctx.send("Not registered. Use `/register <webhook_url>` first.")
        return

    await ctx.send(
        f"**Your settings**\n"
        f"Webhook: {settings['webhook_preview']}\n"
        f"Registered: {settings['created_at']}\n"
        f"Paused: {settings['paused']}\n"
        f"Cities: {', '.join(settings['cities']) or 'none'}\n"
        f"Countries: {', '.join(settings['countries']) or 'none'}\n"
        f"Club IDs: {', '.join(settings['club_ids']) or 'none'}"
    )


@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("Tracker online.")


@bot.command(name="add")
async def add(ctx, *, city: str):
    if not await ensure_registered(ctx):
        return
    if add_city(uid(ctx), city):
        await ctx.send(f"Added city: {city}")
    else:
        await ctx.send(f"City already watched: {city}")


@bot.command(name="remove")
async def remove(ctx, *, city: str):
    if not await ensure_registered(ctx):
        return
    if remove_city(uid(ctx), city):
        await ctx.send(f"Removed city: {city}")
    else:
        await ctx.send(f"City not in watchlist: {city}")


@bot.command(name="list")
async def list_cmd(ctx):
    if not await ensure_registered(ctx):
        return
    data = list_watchlist(uid(ctx))
    await ctx.send(
        f"**Your watchlist**\n"
        f"Paused: {data['paused']}\n"
        f"Cities: {', '.join(data['cities']) or 'none'}\n"
        f"Countries: {', '.join(data['countries']) or 'none'}\n"
        f"Club IDs: {', '.join(data['club_ids']) or 'none'}"
    )


@bot.command(name="pause")
async def pause(ctx):
    if not await ensure_registered(ctx):
        return
    pause_notifications(uid(ctx))
    await ctx.send("Your notifications are paused.")


@bot.command(name="resume")
async def resume(ctx):
    if not await ensure_registered(ctx):
        return
    resume_notifications(uid(ctx))
    await ctx.send("Your notifications are resumed.")


@bot.command(name="status")
async def status(ctx):
    if not await ensure_registered(ctx):
        return
    data = get_status(uid(ctx))
    await ctx.send(
        f"Paused: {data['paused']}\n"
        f"Cities watched: {data['cities']}\n"
        f"Countries watched: {data['countries']}\n"
        f"Club IDs watched: {data['club_ids']}"
    )


@bot.command(name="watchall")
async def watchall(ctx):
    if not await ensure_registered(ctx):
        return
    enable_watchall(uid(ctx))
    await ctx.send("You are now watching all cities.")


@bot.command(name="country")
async def country(ctx, *, country_name: str):
    if not await ensure_registered(ctx):
        return
    if add_country(uid(ctx), country_name):
        await ctx.send(f"Added country: {country_name.upper()}")
    else:
        await ctx.send(f"Country already watched: {country_name.upper()}")


@bot.command(name="country_remove")
async def country_remove(ctx, *, country_name: str):
    if not await ensure_registered(ctx):
        return
    if remove_country(uid(ctx), country_name):
        await ctx.send(f"Removed country: {country_name.upper()}")
    else:
        await ctx.send(f"Country not in watchlist: {country_name.upper()}")


@bot.command(name="country_list")
async def country_list(ctx):
    if not await ensure_registered(ctx):
        return
    countries = get_country_list(uid(ctx))
    await ctx.send(", ".join(countries) if countries else "No countries watched.")


@bot.command(name="clubid")
async def clubid(ctx, club_id: str):
    if not await ensure_registered(ctx):
        return
    if add_club_id(uid(ctx), club_id):
        await ctx.send(f"Added club ID: {club_id}")
    else:
        await ctx.send(f"Club ID already watched: {club_id}")


@bot.command(name="remove_clubid")
async def remove_clubid(ctx, club_id: str):
    if not await ensure_registered(ctx):
        return
    if remove_club_id(uid(ctx), club_id):
        await ctx.send(f"Removed club ID: {club_id}")
    else:
        await ctx.send(f"Club ID not in watchlist: {club_id}")


@bot.command(name="club_list")
async def club_list(ctx):
    if not await ensure_registered(ctx):
        return
    club_ids = get_club_list(uid(ctx))
    await ctx.send(", ".join(club_ids) if club_ids else "No club IDs watched.")


@bot.command(name="recent")
async def recent(ctx, limit: int = 10):
    limit = max(1, min(limit, 20))
    rows = recent_command(limit)
    if not rows:
        await ctx.send("No transfers recorded yet.")
        return

    lines = []
    for row in rows:
        lines.append(
            f"{row['timestamp']} | {row['city']}, {row['country']} | "
            f"{row['manager']} | {row['club_name']} ({row['club_id']})"
        )

    await ctx.send("\n".join(lines))


@bot.command(name="history")
async def history(ctx, *, city: str):
    rows = history_command(city)
    if not rows:
        await ctx.send("No history found.")
        return

    lines = []
    for row in rows[:10]:
        lines.append(
            f"{row['timestamp']} | {row['city']}, {row['country']} | "
            f"{row['manager']} | {row['club_name']} ({row['club_id']})"
        )

    await ctx.send("\n".join(lines))


@bot.command(name="manager")
async def manager(ctx, *, name: str):
    rows = manager_history(name)
    if not rows:
        await ctx.send("No history found for that manager.")
        return

    lines = []
    for row in rows[:10]:
        lines.append(
            f"{row['timestamp']} | {row['city']}, {row['country']} | "
            f"{row['club_name']} ({row['club_id']})"
        )

    await ctx.send("\n".join(lines))


@bot.command(name="export_history")
async def export_history_cmd(ctx):
    await ctx.send(export_history())


@bot.command(name="rebuild")
async def rebuild(ctx):
    await ctx.send(rebuild_wallet_cache())


@bot.command(name="refresh")
async def refresh(ctx):
    await ctx.send(refresh_now())


@bot.command(name="stats")
async def stats(ctx):
    await ctx.send(stats_command())


@bot.command(name="health")
async def health(ctx):
    await ctx.send(health_command())


@bot.command(name="search")
async def search(ctx, *, query: str):
    parts = query.rsplit(" ", 1)
    limit = 15

    if len(parts) == 2 and parts[1].isdigit():
        search_query = parts[0].strip()
        limit = max(1, min(int(parts[1]), 50))
    else:
        search_query = query.strip()

    if not search_query:
        await ctx.send("Usage: `/search Nashville` or `/search Nashville 30`")
        return

    try:
        matches = search_locations(search_query)
    except Exception as e:
        await ctx.send(f"Search failed: {e}")
        return

    if not matches:
        await ctx.send(f"No locations found matching `{search_query}`.")
        return

    lines = [
        f"Found **{len(matches)}** location(s) matching `{search_query}` "
        f"(showing {min(len(matches), limit)}):"
    ]
    for item in matches[:limit]:
        lines.append(
            f"- {item['city']}, {item['country']} (ID {item['club_id']})"
        )

    if len(matches) > limit:
        lines.append(
            f"...and {len(matches) - limit} more. "
            f"Use `/search {search_query} 50` for more."
        )

    await ctx.send("\n".join(lines))


@bot.command(name="poollog")
async def poollog(ctx, limit: int = 15):
    limit = max(1, min(limit, 30))
    entries = read_pool_log(limit)
    if not entries:
        await ctx.send("No pool departures logged yet.")
        return

    lines = [f"Last **{len(entries)}** pool events:"]
    for entry in entries:
        status = entry.get("status", "unknown")
        city = entry.get("city", "?")
        country = entry.get("country", "?")
        club_id = entry.get("club_id", "?")
        timestamp = entry.get("timestamp", "?")
        line = f"{timestamp} | {status} | {city}, {country} (ID {club_id})"
        if entry.get("manager"):
            line += f" -> {entry['manager']}"
        lines.append(line)

    await ctx.send("\n".join(lines))


@bot.command(name="pending")
async def pending(ctx):
    try:
        rows = get_pending_departures()
    except Exception as e:
        await ctx.send(f"Pending check failed: {e}")
        return

    if not rows:
        await ctx.send("No pending pool departures.")
        return

    lines = [f"**{len(rows)}** location(s) left the pool and are still being tracked:"]
    for row in rows[:20]:
        lines.append(
            f"- {row['city']}, {row['country']} (ID {row['club_id']})"
        )
    if len(rows) > 20:
        lines.append(f"...and {len(rows) - 20} more.")

    await ctx.send("\n".join(lines))


@bot.command(name="club")
async def club(ctx, club_id: str):
    try:
        info = club_info(club_id)
    except Exception as e:
        await ctx.send(f"Club lookup failed: {e}")
        return

    await ctx.send(
        f"**Club {info['club_id']}**\n"
        f"City: {info['city']}, {info['country']}\n"
        f"Owner: {info['manager']}\n"
        f"Wallet: {info['wallet']}\n"
        f"Status: {info['status']}"
    )


@bot.command(name="wallet")
async def wallet(ctx):
    try:
        locations = fetch_locations()
        sample = list(locations.values())[:5]
        lines = [
            f"Pool wallet has **{len(locations)}** locations.",
            "",
            "Sample:",
        ]
        for item in sample:
            lines.append(
                f"- {item['city']}, {item['country']} (ID {item['club_id']})"
            )
        await ctx.send("\n".join(lines))
    except Exception as e:
        await ctx.send(f"Wallet check failed: {e}")


@bot.command(name="version")
async def version_cmd(ctx):
    await ctx.send(f"Version {version()}")


def run_bot():
    if not DISCORD_TOKEN:
        log_error("DISCORD_TOKEN missing; bot cannot start.")
        return

    while True:
        try:
            log_info("Connecting Discord bot...")
            bot.run(DISCORD_TOKEN, log_handler=None, reconnect=True)
        except Exception as e:
            log_error(f"Discord bot crashed: {e}")

        log_info("Discord bot restarting in 30 seconds...")
        time.sleep(30)
