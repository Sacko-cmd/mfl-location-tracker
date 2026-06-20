import discord

from discord.ext import commands

from config import (
    DISCORD_TOKEN
)

from history import (
    get_city_history
)


intents = (
    discord.Intents.default()
)

bot = commands.Bot(

    command_prefix="/",

    intents=intents

)


@bot.command()

async def history(

        ctx,

        *,

        city

):

    rows = get_city_history(
        city
    )

    if not rows:

        await ctx.send(
            "No history found."
        )

        return

    lines = []

    for row in rows[:10]:

        lines.append(

            f"{row[1]} | "

            f"{row[2]} | "

            f"{row[5]}"

        )

    await ctx.send(

        "\n".join(
            lines
        )

    )


@bot.command()

async def ping(
        ctx
):

    await ctx.send(
        "Tracker online."
    )


def run_bot():

    bot.run(
        DISCORD_TOKEN
    )