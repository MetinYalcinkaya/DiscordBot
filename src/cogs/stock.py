import asyncio
import time

import discord
from bs4 import BeautifulSoup
from discord.ext import commands

import db.utils as db


class Stock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="add")
    async def add_watching(self, ctx, url):
        # check if user is in db
        if db.get_user(ctx.author) == None:
            print("User doesn't exist, adding to database")
            db.add_user(ctx.author)
        else:
            print("User already exists")

        # check if stock is in db for user
        if db.get_stock(ctx.author, url) == None:
            print("Stock not watched, adding")
            await ctx.send(f"Adding {url} to your watching!")
            db.add_stock(ctx.author, url)
        else:
            print("Stock already watched")
            await ctx.send(f"{url} is already being watched!")


def setup(bot):
    bot.add_cog(Stock(bot))


async def check_stock():
    start = time.time()
    while True:
        print(f"Time: {time.time() - start:.2f}")
        await asyncio.sleep(1)
