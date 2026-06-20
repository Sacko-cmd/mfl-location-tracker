import discord


def build_embed(

        city,
        country,

        manager,
        wallet,

        club_name,
        club_id

):

    embed = discord.Embed(

        title="🚨 NEW LOCATION CLAIMED",

        color=0x00FF00

    )

    embed.add_field(

        name="City",

        value=city,

        inline=False

    )

    embed.add_field(

        name="Country",

        value=country,

        inline=False

    )

    embed.add_field(

        name="Manager",

        value=manager,

        inline=False

    )

    embed.add_field(

        name="Wallet",

        value=wallet,

        inline=False

    )

    embed.add_field(

        name="Club",

        value=club_name,

        inline=False

    )

    embed.add_field(

        name="Club ID",

        value=str(
            club_id
        ),

        inline=False

    )

    return embed