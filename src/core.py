import os
import sys
from pathlib import Path
from typing import cast

import discord
from discord.ext import commands

import config


def get_prefixes(bot, message):
    cog_prefixes = (cog.prefix for cog in bot.cogs.values() if hasattr(cog, "prefix"))
    default_prefixes = "!"
    return (*cog_prefixes, *default_prefixes)


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(
    command_prefix=get_prefixes,
    intents=intents,
    commands=commands.dm_only(),  # TODO: change this to not only be dms when ready
)

cogs_list = ["stock", "coinflip"]

for cog in cogs_list:
    bot.load_extension(f"cogs.{cog}")


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")


@bot.event
async def on_error(*_: object) -> None:
    handle_error(cast(BaseException, sys.exc_info()[1]))


def handle_error(error: BaseException) -> None:
    if _is_rate_limit(error):
        os.execv(
            sys.executable,
            (
                "python",
                Path(__file__).parent / "__main__.py",
                *sys.argv[1:],
                "--rate-limit-delay",
            ),
        )


# @bot.command(name="add")
# async def add_watching(ctx):
#     await ctx.send("Added")
#     print(f"hello, {ctx.author}")


def _is_rate_limit(error: BaseException) -> bool:
    if isinstance(error, discord.ApplicationCommandInvokeError):
        error = error.original
    return isinstance(error, discord.HTTPException) and error.status == 429


bot.run(config.BOT_TOKEN)
