import discord
from discord.ext import commands

from config import DISCORD_TOKEN
from commands.add import add_city
from commands.club_list import get_club_list
from commands.clubid import add_club_id, remove_club_id
from commands.country import add_country, remove_country
from commands.country_list import get_country_list
from commands.export_history import export_history
from commands.health import health_command
from commands.help import help_text
from commands.history import history_command, recent_command
from commands.list import list_watchlist
from commands.manager import manager_history
from commands.pause import pause_notifications, resume_notifications
from commands.rebuild_wallet_cache import rebuild_wallet_cache
from commands.refresh_now import refresh_now
from commands.remove import remove_city
from commands.stats import stats_command
from commands.status import get_status
from commands.version import version
from commands.watchall import enable_watchall
from logger import log_error, log_info

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents, help_command=None)


@bot.event
async def on_ready():
    log_info(f"Discord bot logged in as {bot.user} (ID {bot.user.id})")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing argument. Try `/help` for usage.")
        return

    if isinstance(error, commands.CommandNotFound):
        return

    log_error(f"Discord command error: {error}")
    await ctx.send(f"Command failed: {error}")


@bot.command(name="help")
async def help_cmd(ctx):
    await ctx.send(help_text())


@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("Tracker online.")


@bot.command(name="add")
async def add(ctx, *, city: str):
    if add_city(city):
        await ctx.send(f"Added city: {city}")
    else:
        await ctx.send(f"City already watched: {city}")


@bot.command(name="remove")
async def remove(ctx, *, city: str):
    if remove_city(city):
        await ctx.send(f"Removed city: {city}")
    else:
        await ctx.send(f"City not in watchlist: {city}")


@bot.command(name="list")
async def list_cmd(ctx):
    data = list_watchlist()
    await ctx.send(
        f"**Watchlist**\n"
        f"Paused: {data['paused']}\n"
        f"Cities: {', '.join(data['cities']) or 'none'}\n"
        f"Countries: {', '.join(data['countries']) or 'none'}\n"
        f"Club IDs: {', '.join(data['club_ids']) or 'none'}"
    )


@bot.command(name="pause")
async def pause(ctx):
    pause_notifications()
    await ctx.send("Notifications paused.")


@bot.command(name="resume")
async def resume(ctx):
    resume_notifications()
    await ctx.send("Notifications resumed.")


@bot.command(name="status")
async def status(ctx):
    data = get_status()
    await ctx.send(
        f"Paused: {data['paused']}\n"
        f"Cities watched: {data['cities']}\n"
        f"Countries watched: {data['countries']}\n"
        f"Club IDs watched: {data['club_ids']}"
    )


@bot.command(name="watchall")
async def watchall(ctx):
    enable_watchall()
    await ctx.send("Now watching all cities.")


@bot.command(name="country")
async def country(ctx, *, country_name: str):
    if add_country(country_name):
        await ctx.send(f"Added country: {country_name.upper()}")
    else:
        await ctx.send(f"Country already watched: {country_name.upper()}")


@bot.command(name="country_remove")
async def country_remove(ctx, *, country_name: str):
    if remove_country(country_name):
        await ctx.send(f"Removed country: {country_name.upper()}")
    else:
        await ctx.send(f"Country not in watchlist: {country_name.upper()}")


@bot.command(name="country_list")
async def country_list(ctx):
    countries = get_country_list()
    await ctx.send(", ".join(countries) if countries else "No countries watched.")


@bot.command(name="clubid")
async def clubid(ctx, club_id: str):
    if add_club_id(club_id):
        await ctx.send(f"Added club ID: {club_id}")
    else:
        await ctx.send(f"Club ID already watched: {club_id}")


@bot.command(name="remove_clubid")
async def remove_clubid(ctx, club_id: str):
    if remove_club_id(club_id):
        await ctx.send(f"Removed club ID: {club_id}")
    else:
        await ctx.send(f"Club ID not in watchlist: {club_id}")


@bot.command(name="club_list")
async def club_list(ctx):
    club_ids = get_club_list()
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


@bot.command(name="version")
async def version_cmd(ctx):
    await ctx.send(f"Version {version()}")


def run_bot():
    if not DISCORD_TOKEN:
        log_error("DISCORD_TOKEN missing; bot cannot start.")
        return

    bot.run(DISCORD_TOKEN, log_handler=None)
