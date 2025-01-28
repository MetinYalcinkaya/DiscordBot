import asyncio
import os
import sys
from pathlib import Path
from typing import cast

import discord
from discord.ext import commands

import config
from cogs.stock import auto_check_stock
from db.connect import try_connect

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

cogs_list = ["stock", "coinflip"]


class Cheeky(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=commands.when_mentioned_or("!"),
            intents=intents,
            commands=commands.dm_only(),
        )

    async def on_ready(self):
        print(f"{self.user} is ready and online!")
        # Inialise functionality
        await self.load_db()
        await self.load_cogs()
        # create task for auto checking stock
        self.loop.create_task(auto_check_stock(self))

    async def load_cogs(self) -> None:
        cogs = cogs_list
        for cog in cogs:
            self.load_extension(f"cogs.{cog}")

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
    if isinstance(error, discord.ApplicationCommandInvokeError):
        error = error.original
    return isinstance(error, discord.HTTPException) and error.status == 429


def run_bot():
    bot = Cheeky()
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(bot.start(config.BOT_TOKEN))
    except KeyboardInterrupt:
        print("\nKeyboard Interrupt. Shutting down...")
    finally:
        if not bot.is_closed():
            print("Bot is shutting down.")
            loop.run_until_complete(bot.close())
            loop.close()
            sys.exit(0)
