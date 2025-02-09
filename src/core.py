import asyncio
import logging
import logging.handlers
import sys
from os import listdir
from os.path import isfile, join
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

COGS_DIR = Path(__file__).parent.joinpath("cogs")

MY_GUILD = discord.Object(id=config.MY_GUILD_ID)

logger = logging.getLogger(__name__)

# Logging setup
file_handler = logging.handlers.RotatingFileHandler(
    filename="discord.log",
    encoding="utf-8",
    maxBytes=32 * 1024 * 1024,
    backupCount=5,
    mode="w",
)
dt_format = "%Y-%m-%d %H:%M:%S"
formatter = logging.Formatter(
    "[{asctime}] [{levelname:<8}] {name}: {message}", dt_format, style="{"
)

file_handler.setFormatter(formatter)

logging.basicConfig(level=logging.DEBUG, handlers=[file_handler])
logging.getLogger("discord").setLevel(logging.DEBUG)


class Cheeky(commands.Bot):
    def __init__(self) -> None:
        super().__init__(intents=intents, command_prefix="!")

    async def on_ready(self):
        print(f"{self.user} is ready and online!")
        await self.load_cogs()
        await self.load_db()
        # create task for auto checking stock
        self.loop.create_task(auto_check_stock(self))
        try:
            await self.tree.sync()
        except Exception as e:
            print(f"Error syncing tree: {e}")

    # async def setup_hook(self):
    #     print(f"Copying global to {config.MY_GUILD_ID}")
    #     await self.tree.sync(guild=MY_GUILD)

    async def load_cogs(self) -> None:
        """
        Traverse /cogs/ directory, getting all files except __init__.py,
        and loads them in to the bot
        """
        cogs = [
            cog.split(".")[0]
            for cog in listdir(COGS_DIR)
            if isfile(join(COGS_DIR, cog)) and cog != "__init__.py"
        ]
        for cog in cogs:
            try:
                await self.load_extension(f"cogs.{cog}")
                print(f"Loaded cog: {cog}")
            except Exception as e:
                print(f"Failed to load cog {cog}: {e}")

    async def on_error(*_: object) -> None:
        handle_error(cast(BaseException, sys.exc_info()[1]))

    async def load_db(self) -> None:
        try_connect()

    async def on_app_command_error(
        self,
        interaction: discord.Interaction,
        error: discord.app_commands.AppCommandError,
    ):
        if not interaction.response.is_done():
            await interaction.response.send_message(
                "Command was unable to be executed", ephemeral=True
            )
            logger.error(f"Error executing command: {error}")


def handle_error(error: BaseException) -> None:
    print(f"{error}")


def run_bot():
    if not config.BOT_TOKEN or config.BOT_TOKEN == 0:
        raise ValueError("BOT_TOKEN must be set in config")

    bot = Cheeky()
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(bot.start(config.BOT_TOKEN, reconnect=True))
    except KeyboardInterrupt:
        print("\nKeyboard Interrupt. Shutting down...")
    finally:
        if not bot.is_closed():
            print("Bot is shutting down.")
            loop.run_until_complete(bot.close())
            loop.close()
            sys.exit(0)
