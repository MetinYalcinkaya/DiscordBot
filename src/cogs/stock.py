import asyncio
import json
import logging
import re
from datetime import datetime
from enum import Enum
from typing import List, Optional

import discord
from async_lru import alru_cache
from bs4 import BeautifulSoup
from discord import app_commands
from discord.ext import commands
from playwright.async_api import async_playwright
from price_parser import Price

import db.utils as db
from config import MY_USER_ID
from db.connect import Session
from db.models import User_Stock  # TODO: maybe import User

logger = logging.getLogger(__name__)

SYMBOL_INFO = {
    # Symbols and their positioning
    "$": "prefix",
    "£": "prefix",
    "¥": "prefix",
    "₹": "prefix",
    "€": "suffix",
    "kr": "suffix",
    "zł": "suffix",
    "₩": "prefix",
    "₺": "prefix",
    "₪": "prefix",
    "Ft": "suffix",
    "Kč": "suffix",
    "₽": "suffix",
}

ISO_TO_SYMBOL = {
    # ISO codes to symbols
    "USD": "$",
    "AUD": "$",
    "CAD": "$",
    "GBP": "£",
    "JPY": "¥",
    "INR": "₹",
    "EUR": "€",
    "SEK": "kr",
    "NOK": "kr",
    "DKK": "kr",
    "PLN": "zł",
    "CZK": "Kč",
    "HUF": "Ft",
    "RUB": "₽",
}


class Stock(commands.Cog, name="Stock Watcher"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    stock = app_commands.Group(
        name="stock", description="Manage your product watchlist"
    )

    @stock.command(name="add", description="Add a product to your watchlist")
    @app_commands.describe(
        url="The URL of the product to add", name="The name of the stock"
    )
    async def add_watching(
        self, interaction: discord.Interaction, url: str, name: Optional[str]
    ):
        # check if user is in db
        if db.get_user(interaction.user) is None:
            logger.info(
                f"User {interaction.user.id}:{interaction.user.name} isn't in database, adding"
            )
            db.add_user(interaction.user)
        else:
            logger.info(
                f"User {interaction.user.id}:{interaction.user.name} already exists in database"
            )

        await interaction.response.defer(ephemeral=True, thinking=True)

        # check if stock is in db for user
        if get_stock(interaction.user, url) is None:
            logger.info(f"Stock {url} not watched for user {interaction.user}, adding")

            if name is None:
                try:
                    name = await get_stock_name(url)
                except Exception as e:
                    logger.error(f"Could not get stock name for {url}: {e}")

            await interaction.edit_original_response(
                content=f"Adding [{name}](<{url}>) to your watchlist!"
            )
            try:
                await add_stock(interaction.user, url, name)
            except Exception as e:
                logger.info(f"Could not add stock to database: {e}")
                await interaction.edit_original_response(
                    content=f"There was an error adding your product to the database, please report this error with the URL for the product: [URL](<{url}>)"
                )
        else:
            logger.info(f"Stock {url} already watched for user {interaction.user.id}")
            name = get_stock(interaction.user, url).stock_name
            await interaction.edit_original_response(
                content=f"[{name}](<{url}>) is already being watched!"
            )

    # TODO: Add remove functionality
    # @app_commands.describe(number="The index of the stock you wish to remove")
    @stock.command(name="remove", description="Remove a product from your watchlist")
    async def remove_watching(self, interaction: discord.Interaction):
        # TODO: get watched stocks for given user, give them an index
        # and create buttons the user can interact with based on that

        watched_stocks = await get_users_watched(interaction.user)
        for index, stock in enumerate(watched_stocks):
            print("temp")

        print("Hello, world!")

    @stock.command(name="list", description="List all product in your watchlist")
    async def list_watching(self, interaction: discord.Interaction):
        items = await get_users_watched(interaction.user)
        if not items:
            await interaction.response.send_message(
                "You're not watching any items!", ephemeral=True
            )
            return
        # bot_message = await interaction.response.send_message(
        #     "# Watched Items\n", ephemeral=True
        # )
        bot_message = "# Watched Items\n"
        for index, item in enumerate(items):
            in_stock = "In stock" if item.stock_status == 1 else "Out of stock"
            bot_message += f"**{index + 1}**: _[{item.stock_name}](<{item.stock_url}>)_: **{in_stock}** **{item.price}**\n"
            # await interaction.response.edit_message("test")
            # # bot_message = await interaction.response.edit_message(
            #     content=bot_message.content + message
            # )
        await interaction.response.send_message(bot_message, ephemeral=True)

    # # functionality testing
    # @stock.command(name="test", description="Test functionality")
    # async def test(self, interaction: discord.Interaction):
    #     print("Attempting to execute test function")
    #     if interaction.user.id == MY_USER_ID:
    #         print(
    #             f"Authorised user: {interaction.user.name} - ID: {interaction.user.id}"
    #         )
    #         print("\n\n--------------- Testing ---------------\n\n")
    #         # soup = await fetch_page_contents(
    #         #     "https://supernote.au/shop/p/supernote-manta"
    #         # )
    #         soup = await fetch_page_contents("https://kriticalpads.com/evga-3080-ftw3")
    #
    #         # Regex to find price regardless of if it's a prefix or suffix
    #         price_regex = re.compile(
    #             r"(?:"
    #             r"(?:[\$\£\¥\₹]\s?\d+(?:[.,]\d+)?)"  # e.g. $9.99, ¥ 1000, ₹50, etc.
    #             r"|"
    #             r"(?:\d+(?:[.,]\d+)?\s?(?:€|kr|zł))"  # e.g. 9.99€, 1000 kr, 50zł, etc.
    #             r")",
    #             re.IGNORECASE,
    #         )
    #         potential_prices = soup.find_all(
    #             lambda tag: tag.string and re.search(price_regex, tag.string)
    #         )
    #         if potential_prices:
    #             price_text = potential_prices[0].get_text(strip=True)
    #             print(price_text)
    #
    #         try:
    #             user = self.bot.get_user(MY_USER_ID)
    #             if user is None:
    #                 user = await self.bot.fetch_user(MY_USER_ID)
    #
    #             await user.send("Hello!")
    #         except Exception as e:
    #             print(f"Error sending message: {e}")

    @commands.Cog.listener()
    async def on_application_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        if isinstance(error, commands.NotOwner):
            await interaction.response.send_message(
                "You don't have permission to use that command"
            )
        else:
            raise error  # raises the other errors


class Stock_Status(Enum):
    """
    OUT_OF_STOCK = 0
    IN_STOCK     = 1
    """

    OUT_OF_STOCK = 0
    IN_STOCK = 1


async def auto_check_stock(bot: commands.Bot, interval: int = 60):
    logger.info("Starting automatic stock checking")
    while True:
        # TODO: check for duplicate url's and filter them
        all_stocks = await get_all_watched()
        for stock in all_stocks:
            # try get user from cache, otherwise fetch directly
            user = bot.get_user(stock.user_id)
            if user is None:
                user = await bot.fetch_user(stock.user_id)

            logger.info(f"Checking stock {stock.stock_url}")

            time_passed = (datetime.now() - stock.last_checked).total_seconds()
            if time_passed >= stock.check_interval:
                stock_status = await check_stock(stock.stock_url) == 1
                price = await get_stock_price(stock.stock_url)
                await update_last_checked(stock)
                await update_stock_status(stock, stock_status)
                if stock_status != stock.stock_status:
                    in_stock_message = (
                        "In stock" if stock_status == 1 else "Out of stock"
                    )
                    message = f"{stock.stock_name} is now **{in_stock_message}**!"
                    await user.send(message)
                if price != stock.price:
                    message = f"[{stock.stock_name}](<{stock.stock_url}>) price change: {stock.price} -> {price}"
                    await update_stock_price(stock, price)
                    await user.send(message)

            else:
                logger.info(f"No need to check {stock.stock_url}")
        await asyncio.sleep(interval)


async def check_stock(url: str) -> int:
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
        logger.info(f"Product {url} was found in stock")
        return Stock_Status.IN_STOCK.value
    else:
        logger.info(f"Product {url} was found out of stock")
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
        try:
            await page.goto(url, wait_until="networkidle")
        except Exception as e:
            logger.error(f"Error navigating to webpage {url}: {e}")
        html = await page.content()
        await browser.close()

    soup = BeautifulSoup(html, "html.parser")
    # [s.extract() for s in soup(["style", "script", "[document]", "head", "title"])]

    return soup


async def add_stock(user: discord.Member, url: str, stock_name: str):
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


def get_stock(user: discord.Member, url: str) -> User_Stock | None:
    with Session() as session:
        return (
            session.query(User_Stock)
            .filter(User_Stock.user_id == user.id, User_Stock.stock_url == url)
            .one_or_none()
        )


@alru_cache(maxsize=100)
async def get_stock_price(url: str) -> str:
    """
    Finds the price of given products url: str and returns it formatted.
    """
    soup = await fetch_page_contents(url)

    # helper function to format currency
    def format_price(currency_code, price) -> str:
        symbol = ISO_TO_SYMBOL.get(currency_code, currency_code)
        position = SYMBOL_INFO.get(symbol, "prefix")
        return f"{symbol}{price}" if position == "prefix" else f"{price}{symbol}"

    # check schema.org meta tags
    price_meta = soup.find("meta", itemprop="price")
    currency_meta = soup.find("meta", itemprop="priceCurrency")
    if price_meta and currency_meta:
        return format_price(currency_meta["content"], price_meta["content"])

    # check opengraph meta tags
    price_og = soup.find("meta", property="product:price:amount")
    currency_og = soup.find("meta", property="product:price:currency")
    if price_og and currency_og:
        return format_price(currency_og["content"], price_og["content"])

    # check json-ld data
    json_data = _extract_price_from_json_ld(soup)
    if json_data and "price" in json_data and "currency" in json_data:
        return format_price(json_data["currency"], json_data["price"])

    # common elements by class name
    price_classes = re.compile(
        r"price|product-price|amount|product__price", re.IGNORECASE
    )
    price_element = soup.find_all(class_=price_classes)
    for element in price_element:
        parsed_price = _parse_price_string(element.get_text(strip=True))
        if parsed_price:
            logger.info(f"Found common elements for {url}")
            return parsed_price

    # fallback to parsing entire page text
    page_text = soup.get_text()
    parsed_price = _parse_price_string(page_text)
    if parsed_price:
        logger.info(f"Fallback to parse entire page for {url}")
        return parsed_price

    # regex fallback
    price_regex = re.compile(
        r"(?:[\$\£\¥\₹]\s?\d+[\d.,]*)|(?:\d+[\d.,]*\s?[€]|kr|zł)", re.IGNORECASE
    )
    potential_prices = soup.find_all(string=price_regex)
    for text in potential_prices:
        parsed_price = _parse_price_string(text.strip())
        if parsed_price:
            logger.info(f"Fallback to regex for {url}")
            return parsed_price

    return "Price not found"


def _parse_price_string(text: str) -> str | None:
    """
    Parses the given text:str and finds the product price if it is found, otherwise returns None
    """
    price = Price.fromstring(text)
    if price and price.amount_float:
        currency = price.currency.strip()
        amount = price.amount_text

        symbol = ISO_TO_SYMBOL.get(currency, currency)
        position = SYMBOL_INFO.get(symbol, "prefix")
        return f"{symbol}{amount}" if position == "prefix" else f"{amount}{symbol}"

    return None


def _extract_price_from_json_ld(soup: BeautifulSoup) -> str | None:
    """
    Extracts the price of a product from the given parsed HTML/XML document, if it is in JSON-LD format
    """
    json_ld = soup.find("script", type="application/ld+json")
    if json_ld:
        try:
            data = json.loads(json_ld.string)
            price = (
                data.get("offers", {}).get("price")
                or data.get("price")
                or data.get("product", {}).get("price")
            )
            return str(price) if price else None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
    return None


async def get_users_watched(user: discord.Member) -> List[User_Stock] | None:
    """
    Gets all the given discord.Member's User_Stock's and returns as a list or None
    """
    try:
        with Session() as session:
            return session.query(User_Stock).filter(User_Stock.user_id == user.id).all()
    except Exception as e:
        logger.error(f"Error getting users watched: {e}")


async def get_all_watched() -> List[User_Stock] | None:
    """
    Gets all watched User_Stock for every user and returns as a list or None
    """
    with Session() as session:
        try:
            return session.query(User_Stock).filter().all()
        except Exception as e:
            logger.error(f"Error getting all watched: {e}")


async def update_last_checked(stock: User_Stock):
    """
    Updates the given User_Stock.last_checked with the current datetime.now()
    """
    with Session() as session:
        db_stock = stock
        db_stock.last_checked = datetime.now()
        session.add(db_stock)
        session.commit()
        logger.info(f"Last checked updated for {stock.stock_url}")


async def update_stock_status(stock: User_Stock, status: int):
    """
    Update the given User_Stock.stock_status with given status argument
    """
    with Session() as session:
        db_stock = stock
        db_stock.stock_status = status
        session.add(db_stock)
        session.commit()
        logger.info(f"Stock status updated for {stock.stock_url}")


async def update_stock_price(stock: User_Stock, price: str):
    """
    Update the given User_Stock.price with given price argument
    """
    if price is None:
        print(f"Price is None, can't update price for {stock.stock_url}")
        return
    with Session() as session:
        db_stock = stock
        db_stock.price = price
        session.add(db_stock)
        session.commit()
        logger.info(f"Stock price updated for {stock.stock_url}")


# class Button(discord.ui.Button):
#


async def setup(bot):
    await bot.add_cog(Stock(bot))
