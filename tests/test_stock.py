from unittest.mock import AsyncMock, MagicMock

import pytest
from bs4 import BeautifulSoup
from discord import Interaction

from cogs import stock


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


@pytest.mark.asyncio
async def test_fetch_page_contents(monkeypatch):
    async def fake_fetch(url: str) -> BeautifulSoup:
        html = "<html><head><title>Unit Test Title</title></head><html>"
        return BeautifulSoup(html, "html.parser")

    monkeypatch.setattr("cogs.stock.fetch_page_contents", fake_fetch)

    soup = await stock.fetch_page_contents("https://testing.com")
    title = soup.find("title").string
    assert title == "Unit Test Title"


@pytest.mark.asyncio
async def test_check_stock_out_of_stock(monkeypatch):
    async def fake_fetch(url: str) -> int:
        html = '<html><span id="availability" class="product_availability availability-item">Out of Stock</span></html>'
        return BeautifulSoup(html, "html.parser")

    monkeypatch.setattr("cogs.stock.fetch_page_contents", fake_fetch)

    result = await stock.check_stock("https://testing.com")
    assert result == 0


@pytest.mark.asyncio
async def test_check_stock_in_stock(monkeypatch):
    async def fake_fetch(url: str) -> int:
        html = '<html><span id="availability" class="product_availability availability-item">In Stock</span></html>'
        return BeautifulSoup(html, "html.parser")

    monkeypatch.setattr("cogs.stock.fetch_page_contents", fake_fetch)

    result = await stock.check_stock("https://testing.com")
    assert result == 1


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
async def test_add_watching(mocker):
    fake_bot = MagicMock()

    fake_user = MagicMock()
    fake_user.id = 123
    fake_user.name = "Testing"

    fake_interaction = MagicMock(spec=Interaction)
    fake_interaction.user = fake_user
    fake_interaction.response = AsyncMock()

    stock_cog = stock.Stock(fake_bot)

    # patch database funcs to prevent actual database calls
    mocker.patch("cogs.stock.db.get_user", return_value=None)
    mocker.patch("cogs.stock.db.add_user", return_value=None)

    # patch other database funcs or external calls
    mocker.patch("cogs.stock.get_stock", return_value=None)
    mocker.patch("cogs.stock.add_stock", return_value=AsyncMock())
    mocker.patch(
        "cogs.stock.get_stock_name", return_value=AsyncMock(return_value="Test Product")
    )
    await stock_cog.add_watching.callback(
        stock_cog, fake_interaction, url="http://testing.com", name="Test Product"
    )
    fake_interaction.response.defer.assert_called_once()
