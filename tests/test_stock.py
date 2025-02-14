from unittest.mock import AsyncMock, MagicMock

import pytest
from bs4 import BeautifulSoup, Tag
from discord import Interaction, app_commands
from discord.ext import commands

from cogs import stock
from db.models import User, User_Stock


def test_parse_price_string_valid():
    text = "$11.22"
    result = stock._parse_price_string(text)
    assert result == "$11.22"


def test_parse_price_string_valid_with_prefix_text():
    text = "Price: $11.22"
    result = stock._parse_price_string(text)
    assert result == "$11.22"


def test_parse_price_string_valid_with_suffix_text():
    text = "$11.22 Each"
    result = stock._parse_price_string(text)
    assert result == "$11.22"


def test_parse_price_string_valid_with_prefix_and_suffix_text():
    text = "Price: $11.22 Each"
    result = stock._parse_price_string(text)
    assert result == "$11.22"


def test_parse_price_string_invalid():
    text = "No price in this string"
    result = stock._parse_price_string(text)
    assert result is None


def test_parse_price_string_valid_euro():
    text = "2,00€"
    result = stock._parse_price_string(text)
    assert result == "2,00€"


def test_parse_price_string_valid_pound():
    text = "£201.00"
    result = stock._parse_price_string(text)
    assert result == "£201.00"


def test_parse_price_string_valid_jpy():
    text = "¥4,000"
    result = stock._parse_price_string(text)
    assert result == "¥4,000"


@pytest.mark.parametrize(
    "price_text,expected",
    [
        ("$99.99", "$99.99"),
        ("99.99€", "99.99€"),
        ("£199.99", "£199.99"),
        ("¥12000", "¥12000"),
        ("1999 kr", "1999kr"),
        ("Invalid", None),
    ],
)
def test_parse_price_string_formats(price_text, expected):
    result = stock._parse_price_string(price_text)
    assert result == expected


@pytest.mark.asyncio
async def test_fetch_page_contents(monkeypatch):
    async def fake_fetch(url: str) -> BeautifulSoup:
        html = "<html><head><title>Unit Test Title</title></head><html>"
        return BeautifulSoup(html, "html.parser")

    monkeypatch.setattr("cogs.stock.fetch_page_contents", fake_fetch)

    soup = await stock.fetch_page_contents("https://testing.com")
    title = soup.find("title")
    if isinstance(title, Tag):
        title = title.string
    assert title == "Unit Test Title"


@pytest.mark.asyncio
async def test_check_stock_out_of_stock(monkeypatch):
    async def fake_fetch(url: str) -> BeautifulSoup:
        html = '<html><span id="availability" class="product_availability availability-item">Out of Stock</span></html>'
        return BeautifulSoup(html, "html.parser")

    monkeypatch.setattr("cogs.stock.fetch_page_contents", fake_fetch)

    result = await stock.fetch_stock_status("https://testing.com")
    assert result == 0


@pytest.mark.asyncio
async def test_check_stock_in_stock(monkeypatch):
    async def fake_fetch(url: str) -> BeautifulSoup:
        html = '<html><span id="availability" class="product_availability availability-item">In Stock</span></html>'
        return BeautifulSoup(html, "html.parser")

    monkeypatch.setattr("cogs.stock.fetch_page_contents", fake_fetch)

    result = await stock.fetch_stock_status("https://testing.com")
    assert result == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "page_content,expected_status",
    [
        ("<div>In Stock</div>", 1),
        ("<div>Out of Stock</div>", 0),
        ("<div>Sold Out</div>", 0),
        ("<div>Available</div>", 1),
        ("<div>Not Available</div>", 0),
    ],
)
async def test_check_stock_variations(mocker, page_content, expected_status):
    async def fake_fetch(url: str):
        return BeautifulSoup(page_content, "html.parser")

    mocker.patch("cogs.stock.fetch_page_contents", fake_fetch)
    result = await stock.fetch_stock_status("https://testing.com")
    assert result == expected_status


@pytest.mark.asyncio
async def test_get_stock_price_schemaorg(monkeypatch):
    async def fake_fetch(url: str) -> BeautifulSoup:
        html = """
<html>
  <head>
    <meta itemprop="price" content="49.99">
    <meta itemprop="priceCurrency" content="USD">
    <title>Test Product Page</title>
  </head>
  <body>
    <h1>Test Product Title</h1>
    <p>Test product description.</p>
  </body>
</html>
        """
        return BeautifulSoup(html, "html.parser")

    monkeypatch.setattr("cogs.stock.fetch_page_contents", fake_fetch)
    result = await stock.get_stock_price("https://testing.com/product_gsp1")
    assert result == "$49.99"


@pytest.mark.asyncio
async def test_get_stock_price_opengraph(monkeypatch):
    async def fake_fetch(url: str) -> BeautifulSoup:
        html = """
<html>
  <head>
    <meta property="product:price:amount" content="59.99">
    <meta property="product:price:currency" content="USD">
    <title>Product Page</title>
  </head>
  <body>
    <h1>Product Title</h1>
    <p>Product description.</p>
  </body>
</html>
        """
        return BeautifulSoup(html, "html.parser")

    monkeypatch.setattr("cogs.stock.fetch_page_contents", fake_fetch)
    result = await stock.get_stock_price("https://testing.com/product_gsp2")
    assert result == "$59.99"


@pytest.mark.asyncio
async def test_get_stock_price_jsonld(monkeypatch):
    async def fake_fetch(url: str) -> BeautifulSoup:
        html = """
<html>
  <head>
    <script type="application/ld+json">
    {
      "price": "99.99",
      "currency": "USD"
    }
    </script>
    <title>Product Page</title>
  </head>
  <body>
    <h1>Product Title</h1>
    <p>Product description.</p>
  </body>
</html>
        """
        return BeautifulSoup(html, "html.parser")

    monkeypatch.setattr("cogs.stock.fetch_page_contents", fake_fetch)
    result = await stock.get_stock_price("https://testing.com/product_gsp3")
    assert result == "$99.99"


@pytest.mark.asyncio
async def test_get_stock_price_fallback_entire_page(monkeypatch):
    async def fake_fetch(url: str) -> BeautifulSoup:
        html = """
<html>
  <head>
    <title>Product Page</title>
  </head>
  <body>
    <p>Welcome to our store! Get this amazing product for only $29.99 while supplies last.</p>
  </body>
</html>
        """
        return BeautifulSoup(html, "html.parser")

    monkeypatch.setattr("cogs.stock.fetch_page_contents", fake_fetch)
    result = await stock.get_stock_price("https://testing.com/product_gsp4")
    assert result == "$29.99"


@pytest.mark.asyncio
async def test_get_stock_price_fallback_regex(monkeypatch):
    async def fake_fetch(url: str) -> BeautifulSoup:
        html = """
<html>
  <head>
    <title>Product Page</title>
  </head>
  <body>
    <p>Limited time offer: Special price at £99 for our premium product!</p>
  </body>
</html>
        """
        return BeautifulSoup(html, "html.parser")

    monkeypatch.setattr("cogs.stock.fetch_page_contents", fake_fetch)
    result = await stock.get_stock_price("https://testing.com/product_gsp5")
    assert result == "£99"


@pytest.mark.asyncio
async def test_get_stock_price_no_price(mocker):
    async def fake_fetch(url: str) -> BeautifulSoup:
        html = "<html><body>No price information</body></html>"
        return BeautifulSoup(html, "html.parser")

    mocker.patch("cogs.stock.fetch_page_contents", fake_fetch)
    result = await stock.get_stock_price("https://testing.com")
    assert result == "Price not found"


@pytest.mark.asyncio
async def test_add_watching(mocker):
    bot = MagicMock()

    user = MagicMock()
    user.id = 123
    user.name = "Testing"

    interaction = MagicMock(spec=Interaction)
    interaction.user = user
    interaction.response = AsyncMock()

    stock_cog = stock.Stock(bot)

    # patch database funcs to prevent actual database calls
    mocker.patch("cogs.stock.db.get_user", return_value=None)
    mocker.patch("cogs.stock.db.add_user", return_value=None)

    # patch other database funcs or external calls
    mocker.patch("cogs.stock.get_stock", return_value=None)
    mocker.patch("cogs.stock.add_stock", return_value=AsyncMock())
    mocker.patch(
        "cogs.stock.get_stock_name", return_value=AsyncMock(return_value="Test Product")
    )
    bound_callback = stock_cog.add_watching.callback.__get__(stock_cog, type(stock_cog))
    await bound_callback(interaction, "http://testing.com", "Test Product")
    interaction.response.defer.assert_called_once()


@pytest.mark.asyncio
async def test_add_watching_invalid_url(mocker):
    bot = MagicMock()

    user = MagicMock()
    user.id = 123
    user.name = "Testing"

    interaction = AsyncMock(spec=Interaction)
    interaction.user = user
    interaction.response = AsyncMock()
    # interaction.response.send_message = AsyncMock()
    stock_cog = stock.Stock(bot)

    mocker.patch("cogs.stock.get_stock_name", return_value=None)

    bound_callback = stock_cog.add_watching.callback.__get__(stock_cog, type(stock_cog))
    await bound_callback(interaction, "invalid_url")
    response = interaction.response.send_message.call_args[0][0]

    invalid_string = "invalid url"
    assert invalid_string in response.lower()


@pytest.mark.asyncio
async def test_add_watching_invalid_name(mocker):
    # HACK: v strange way to do this, but it works, maybe refactor?
    bot = MagicMock()

    user = MagicMock()
    user.id = 123
    user.name = "Testing"

    interaction = AsyncMock(spec=Interaction)
    interaction.user = user
    interaction.response = AsyncMock()
    interaction.edit_original_response = AsyncMock()

    stock_cog = stock.Stock(bot)
    fake_user = MagicMock(spec=User)

    mocker.patch("cogs.stock.get_stock", return_value=None)
    mocker.patch("cogs.stock.get_stock_name", return_value=None)
    mocker.patch("db.utils.get_user", return_value=fake_user)
    mocker.patch("db.utils.add_user", return_value=fake_user)

    bound_callback = stock_cog.add_watching.callback.__get__(stock_cog, type(stock_cog))
    await bound_callback(interaction, "https://testing.com")
    response = interaction.edit_original_response.call_args[1]["content"]
    print(f"debug: {response}")

    invalid_string = "manually"
    assert invalid_string in response.lower()


@pytest.mark.asyncio
async def test_list_watching(mocker):
    bot = MagicMock()
    interaction = AsyncMock()
    stock_cog = stock.Stock(bot)

    user_stocks = [
        User_Stock(
            user_id="12345",
            stock_url="http://testing1.com",
            stock_name="Test Product 1",
            stock_status=1,
            date_added="2025-02-04 19:55:13.145789",
            last_checked="2025-02-04 19:55:13.145789",
            check_interval=300,
            price="$123.45",
        ),
        User_Stock(
            user_id="12345",
            stock_url="http://testing2.com",
            stock_name="Test Product 2",
            stock_status=0,
            date_added="2025-02-04 19:55:13.145789",
            last_checked="2025-02-04 19:55:13.145789",
            check_interval=300,
            price="$543.21",
        ),
    ]
    response_string = f"""# Watched Items
**1**: _[{user_stocks[0].stock_name}](<{user_stocks[0].stock_url}>)_: **{"In stock" if user_stocks[0].stock_status == 1 else "Out of stock"}** **{user_stocks[0].price}**
**2**: _[{user_stocks[1].stock_name}](<{user_stocks[1].stock_url}>)_: **{"In stock" if user_stocks[1].stock_status == 1 else "Out of stock"}** **{user_stocks[1].price}**
"""

    mocker.patch("cogs.stock.get_users_watched", return_value=user_stocks)
    bound_callback = stock_cog.list_watching.callback.__get__(
        stock_cog, type(stock_cog)
    )
    await bound_callback(interaction)
    interaction.response.send_message.assert_called_with(
        response_string, ephemeral=True
    )


@pytest.mark.asyncio
async def test_list_watching_empty(mocker):
    bot = MagicMock()
    interaction = AsyncMock()
    stock_cog = stock.Stock(bot)

    mocker.patch("cogs.stock.get_users_watched", return_value=[])
    bound_callback = stock_cog.list_watching.callback.__get__(
        stock_cog, type(stock_cog)
    )
    await bound_callback(interaction)
    interaction.response.send_message.assert_called_with(
        "You're not watching any items!", ephemeral=True
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "error,expected_message",
    [
        (commands.NotOwner(), "You don't have permission to use that command"),
        (app_commands.CommandInvokeError, None),
    ],
)
async def test_command_error_handing(error, expected_message):
    bot = MagicMock()
    interaction = AsyncMock(spec=Interaction)
    interaction.response = AsyncMock()
    interaction.response.send_message = AsyncMock()
    cog = stock.Stock(bot)

    if expected_message is None:
        with pytest.raises(Exception):
            await cog.on_application_command_error(interaction, error)
    else:
        await cog.on_application_command_error(interaction, error)
        interaction.response.send_message.assert_called_with(expected_message)


@pytest.mark.asyncio
async def test_stock_price_update_notif(mocker):
    bot = MagicMock()
    user = MagicMock(id=123)
    user.send = AsyncMock()

    stock_item = MagicMock(
        user_id=123,
        stock_name="Test Product",
        stock_url="https://testing.com",
        price="$5.50",
        stock_status=1,
    )

    mocker.patch("cogs.stock.get_stock_price", return_value="$2.00")
    mocker.patch("cogs.stock.fetch_stock_status", return_value=1)
    mocker.patch("cogs.stock.update_last_checked")
    mocker.patch("cogs.stock.update_stock_status")
    mocker.patch("cogs.stock.update_stock_price")

    bot.get_user.return_value = user

    await stock.check_stock(stock_item, user)

    message = "[Test Product](<https://testing.com>) price change: $5.50 -> $2.00"
    user.send.assert_called_with(message)


@pytest.mark.asyncio
async def test_stock_status_update_notif(mocker):
    bot = MagicMock()
    user = MagicMock(id=123)
    user.send = AsyncMock()

    stock_item = MagicMock(
        user_id=123,
        stock_name="Test Product",
        stock_url="https://testing.com",
        price="$5.50",
        stock_status=1,
    )

    mocker.patch("cogs.stock.get_stock_price", return_value="$5.50")
    mocker.patch("cogs.stock.fetch_stock_status", return_value=0)
    mocker.patch("cogs.stock.update_last_checked")
    mocker.patch("cogs.stock.update_stock_status")
    mocker.patch("cogs.stock.update_stock_price")

    bot.get_user.return_value = user

    await stock.check_stock(stock_item, user)

    message = "Test Product is now **Out of stock**!"
    user.send.assert_called_with(message)
