import asyncio
import re
from datetime import datetime
from enum import Enum
from typing import List

import discord
from bs4 import BeautifulSoup
from discord.ext import commands
from playwright.async_api import async_playwright

import db.utils as db
from config import MY_USER_ID
from db.connect import Session
from db.models import User_Stock  # TODO: maybe import User

CURRENCY_SYMBOLS = {
    "$": "prefix",
    "£": "prefix",
    "¥": "prefix",
    "₹": "prefix",
    "€": "suffix",
    "kr": "suffix",
    "zł": "suffix",
}


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
        items = get_users_watched(ctx.author)
        if not items:
            await ctx.reply("You're not watching any items!")
            return
        bot_message = await ctx.reply("# Watched Items\n")
        for index, item in enumerate(items):
            in_stock = "In stock" if item.stock_status == 1 else "Out of stock"
            message = f"\n**{index + 1}**: _[{item.stock_name}](<{item.stock_url}>)_: **{in_stock}** **{item.price}**\n"
            bot_message = await bot_message.edit(content=bot_message.content + message)

    # functionality testing
    @stock.command(name="test")
    async def test(self, ctx):
        print("Attempting to execute test function")
        if ctx.author.id == MY_USER_ID:
            print(f"Authorised user: {ctx.author.name} - ID: {ctx.author.id}")
            print("\n\n\n--------------- Testing ---------------\n\n\n")
            # soup = await fetch_page_contents(
            #     "https://supernote.au/shop/p/supernote-manta"
            # )
            soup = await fetch_page_contents("https://kriticalpads.com/evga-3080-ftw3")

            # Regex to find price regardless of if it's a prefix or suffix
            price_regex = re.compile(
                r"(?:"
                r"(?:[\$\£\¥\₹]\s?\d+(?:[.,]\d+)?)"  # e.g. $9.99, ¥ 1000, ₹50, etc.
                r"|"
                r"(?:\d+(?:[.,]\d+)?\s?(?:€|kr|zł))"  # e.g. 9.99€, 1000 kr, 50zł, etc.
                r")",
                re.IGNORECASE,
            )
            potential_prices = soup.find_all(
                lambda tag: tag.string and re.search(price_regex, tag.string)
            )
            if potential_prices:
                price_text = potential_prices[0].get_text(strip=True)
                print(price_text)


def setup(bot):
    bot.add_cog(Stock(bot))


class Stock_Status(Enum):
    OUT_OF_STOCK = 0
    IN_STOCK = 1


async def auto_check_stock(bot, interval: int = 60):
    print("Executing automatic stock checking")
    while True:
        # TODO: check for duplicate url's and filter them
        all_stocks = await get_all_watched()
        for stock in all_stocks:
            # try get user from cache, otherwise fetch directly
            user = bot.get_user(stock.user_id)
            if user is None:
                user = await bot.fetch_user(stock.user_id)

            print(f"Checking stock {stock.stock_url}")

            time_passed = (datetime.now() - stock.last_checked).total_seconds()
            if time_passed >= stock.check_interval:
                stock_status = await check_stock(stock.stock_url) == 1
                await update_last_checked(stock)
                await update_stock_status(stock, stock_status)
                if stock_status != stock.stock_status:
                    in_stock_message = (
                        "In stock" if stock_status == 1 else "Out of stock"
                    )
                    message = f"{stock.stock_name} is now **{in_stock_message}**!"
                    await user.send(message)

            else:
                print(f"No need to check {stock.stock_url}")
        await asyncio.sleep(interval)


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
    price = await get_stock_price(url)

    with Session() as session:
        db_stock = User_Stock(
            user_id=user.id,
            stock_url=url,
            stock_name=stock_name,
            stock_status=stock_status,
            date_added=date_added,
            last_checked=last_checked,
            check_interval=check_interval,
            price=price,
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


async def get_stock_price(url) -> str:
    soup = await fetch_page_contents(url)

    # Regex to find price regardless of if it's a prefix or suffix
    price_regex = re.compile(
        r"(?:"
        r"(?:[\$\£\¥\₹]\s?\d+(?:[.,]\d+)?)"  # e.g. $9.99, ¥ 1000, ₹50, etc.
        r"|"
        r"(?:\d+(?:[.,]\d+)?\s?(?:€|kr|zł))"  # e.g. 9.99€, 1000 kr, 50zł, etc.
        r")",
        re.IGNORECASE,
    )
    potential_prices = soup.find_all(
        lambda tag: tag.string and re.search(price_regex, tag.string)
    )
    if potential_prices:
        price_text = potential_prices[0].get_text(strip=True)
        # print(price_text)
        return price_text


def get_users_watched(user: discord.Member) -> List[User_Stock] | None:
    with Session() as session:
        return session.query(User_Stock).filter(User_Stock.user_id == user.id).all()


# All watched stock regardless of user
async def get_all_watched() -> List[User_Stock] | None:
    with Session() as session:
        return session.query(User_Stock).filter().all()


async def update_last_checked(stock: User_Stock):
    with Session() as session:
        print(f"initial last checked: {stock.last_checked}")
        db_stock = stock
        db_stock.last_checked = datetime.now()
        session.add(db_stock)
        session.commit()
        print("Last checked updated")


async def update_stock_status(stock: User_Stock, status: int):
    with Session() as session:
        db_stock = stock
        db_stock.stock_status = status
        session.add(db_stock)
        session.commit()
        print("Stock status updated")
