import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import cast

import discord
from discord import app_commands
from discord.ext import commands

import config
from cogs.stock import auto_check_stock
from db.connect import try_connect

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

cogs_list = ["stock", "rng"]

MY_GUILD = discord.Object(id=config.MY_GUILD_ID)

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")


class Cheeky(commands.Bot):
    def __init__(self) -> None:
        super().__init__(intents=intents, command_prefix="!")
        # super().__init__(
        #     # TODO: move from dm_only() when ready
        #     command_prefix=commands.when_mentioned_or("!"),
        #     intents=intents,
        #     commands=commands.dm_only(),
        # )
        # self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        print(f"{self.user} is ready and online!")
        # Inialise functionality
        await self.load_db()
        await self.load_cogs()
        await self.setup_hook()
        await self.tree.sync()
        # create task for auto checking stock
        self.loop.create_task(auto_check_stock(self))

    async def load_cogs(self) -> None:
        # TODO: rather than hard coding, traverse cogs dir to get cogs
        cogs = cogs_list
        for cog in cogs:
            try:
                await self.load_extension(f"cogs.{cog}")
                print(f"Loaded cog: {cog}")
            except Exception as e:
                print(f"Failed to load cog {cog}: {e}")

    async def setup_hook(self):
        print(f"Copying global to {config.MY_GUILD_ID}")
        self.tree.copy_global_to(guild=MY_GUILD)

    async def on_error(*_: object) -> None:
        handle_error(cast(BaseException, sys.exc_info()[1]))

    async def load_db(self) -> None:
        try_connect()


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


def _is_rate_limit(error: BaseException) -> bool:
    if isinstance(error, discord.app_commands.CommandInvokeError):
        error = error.original
    return isinstance(error, discord.HTTPException) and error.status == 429


def run_bot():
    bot = Cheeky()
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            bot.run(config.BOT_TOKEN, log_handler=handler, log_level=logging.DEBUG)
        )
    except KeyboardInterrupt:
        print("\nKeyboard Interrupt. Shutting down...")
    finally:
        if not bot.is_closed():
            print("Bot is shutting down.")
            loop.run_until_complete(bot.close())
            loop.close()
            sys.exit(0)
