import re
from datetime import datetime
from enum import Enum
from typing import List

import discord
from bs4 import BeautifulSoup
from discord.ext import commands
from playwright.async_api import async_playwright
from sqlalchemy import select

import db.utils as db
from db.connect import Session
from db.models import User, User_Stock


class Stock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="stock")
    async def stock(self, ctx):
        if ctx.invoked_subcommand is None:
            subcommand_names = ", ".join([cmd.name for cmd in ctx.command.commands])
            await ctx.send(f"Available subcommands: {subcommand_names}")

    @stock.command(name="add")
    async def add_watching(self, ctx, url, name=None):
        # check if user is in db
        if db.get_user(ctx.author) is None:
            print("User doesn't exist, adding to database")
            db.add_user(ctx.author)
        else:
            print("User already exists")

        # check if stock is in db for user
        if get_stock(ctx.author, url) is None:
            print("Stock not watched, adding")

            if name is None:
                name = await get_stock_name(url)

            await ctx.reply(f"Adding [{name}](<{url}>) to your watchlist!")

            await add_stock(ctx.author, url, name)
        else:
            print("Stock already watched")
            await ctx.reply(f"[{name}](<{url}>)is already being watched!")
        # await check_stock(url)

    @stock.command(name="list")
    async def list_watching(self, ctx):
        items = get_all_stocks(ctx.author)
        if not items:
            await ctx.reply("You're not watching any items!")
            return
        # TODO: add timestamp checks
        message = "# Watched Items\n"
        for index, item in enumerate(items):
            if (
                datetime.now() - item.date_added
            ).total_seconds() >= item.check_interval:
                print("big wow time to check")
            in_stock = (
                "In stock" if await check_stock(item.stock_url) == 1 else "Out of stock"
            )
            message += f"**{index+1}**: _[{item.stock_name}](<{item.stock_url}>)_: **{in_stock}**\n"
        await ctx.reply(message)


def setup(bot):
    bot.add_cog(Stock(bot))


class Stock_Status(Enum):
    OUT_OF_STOCK = 0
    IN_STOCK = 1


async def check_stock(url) -> int:
    soup = await fetch_page_contents(url)
    for hidden_element in soup.select("[style*='display:none'], [hidden]"):
        hidden_element.decompose()

    out_of_stock_strings = ["sold out", "out of stock"]
    page_text = soup.get_text().lower()
    in_stock_bool = True

    for string in out_of_stock_strings:
        if string in page_text:
            in_stock_bool = False
            break

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


async def get_stock_name(url: str) -> str | None:
    soup = await fetch_page_contents(url)
    if soup.title is not None:
        if soup.title.string is not None:
            return re.sub(r"\s[—-].*", "", soup.title.string).strip()


async def fetch_page_contents(url: str) -> BeautifulSoup:
    async with async_playwright() as pw:
        # headless browser
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        # user agent
        await page.set_extra_http_headers(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/115.0.0.0 Safari/537.36"
            }
        )
        await page.goto(url, wait_until="networkidle")
        html = await page.content()
        await browser.close()

    soup = BeautifulSoup(html, "html.parser")
    # [s.extract() for s in soup(["style", "script", "[document]", "head", "title"])]

    return soup


async def add_stock(user: discord.Member, url, stock_name):
    stock_status = await check_stock(url)
    date_added = datetime.now()
    last_checked = datetime.now()
    check_interval = 300

    with Session() as session:
        db_stock = User_Stock(
            user_id=user.id,
            stock_url=url,
            stock_name=stock_name,
            stock_status=stock_status,
            date_added=date_added,
            last_checked=last_checked,
            check_interval=check_interval,
        )
        session.add(db_stock)
        session.commit()


def get_stock(user: discord.Member, url) -> User_Stock | None:
    with Session() as session:
        return (
            session.query(User_Stock)
            .filter(User_Stock.user_id == user.id, User_Stock.stock_url == url)
            .one_or_none()
        )


def get_all_stocks(user: discord.Member) -> List[User_Stock] | None:
    with Session() as session:
        # if session.quers
        # if session.query(User).filter(User.user_id == user.id).all() is None:
        #     print("User isn't in the database")
        #     db.add_user(user)
        #     return None
        return session.query(User_Stock).filter(User_Stock.user_id == user.id).all()
