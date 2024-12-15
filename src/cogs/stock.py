import asyncio
import time

import discord
from bs4 import BeautifulSoup
from discord.ext import commands

from src.db.utils import get_user


class Stock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="add")
    async def add_watching(self, ctx, url):
        # first check if user is in db
        if get_user == None:
            print("User doesn't exist")

        print(ctx.author.id)
        await ctx.send(f"Added {url}")


def setup(bot):
    bot.add_cog(Stock(bot))


async def check_stock():
    start = time.time()
    while True:
        print(f"Time: {time.time() - start:.2f}")
        await asyncio.sleep(1)
