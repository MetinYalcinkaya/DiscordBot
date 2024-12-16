from enum import Enum
from urllib.request import Request, urlopen

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
            stock_name = await get_stock_name(url)
            db.add_stock(ctx.author, url, stock_name)
        else:
            print("Stock already watched")
            await ctx.send(f"{url} is already being watched!")
        await check_stock(url)

    @commands.command(name="list")
    async def list_watching(self, ctx):
        items = db.get_all_stocks(ctx.author)
        if not items:
            await ctx.send("You're not watching any items!")
            return

        message = ""
        if items != None:
            for item in items:
                in_stock = (
                    "In stock"
                    if await check_stock(item.stock_url) == 1
                    else "Out of stock"
                )
                message += f"[{item.stock_name}]({item.stock_url}): Current stock: {in_stock}\n"
        await ctx.send(message)


def setup(bot):
    bot.add_cog(Stock(bot))


class Stock_Status(Enum):
    OUT_OF_STOCK = 0
    IN_STOCK = 1


async def check_stock(url) -> int:
    req = Request(url)
    page = urlopen(req).read()

    soup = BeautifulSoup(page, "html.parser")
    out_of_stock_strings = ["sold out", "out of stock"]
    in_stock_bool = True
    for string in out_of_stock_strings:
        if soup.get_text().lower().find(string) != -1:
            in_stock_bool = False

    if in_stock_bool:
        print("Product is in stock!")
        return Stock_Status.IN_STOCK.value
    else:
        print("Product is out of stock")
        return Stock_Status.OUT_OF_STOCK.value

    # start = time.time()
    # while True:
    #     print(f"Time: {time.time() - start:.2f}")
    #     await asyncio.sleep(1)


async def get_stock_name(url) -> str | None:
    req = Request(url)
    page = urlopen(req).read()

    soup = BeautifulSoup(page, "html.parser")
    if soup.title != None:
        return soup.title.string


async def parse_stock_string(string: str) -> dict:
    formatted_dict = dict(item.split("=") for item in string.split("|"))
    return formatted_dict
