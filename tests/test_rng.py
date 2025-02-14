from unittest.mock import AsyncMock, MagicMock

import pytest
from discord import Interaction, app_commands

from cogs import rng


@pytest.mark.asyncio
async def test_flip_coin_default():
    bot = MagicMock()
    interaction = AsyncMock(spec=Interaction)
    interaction.response = AsyncMock()
    interaction.response.send_message = AsyncMock()

    rng_cog = rng.RNG(bot)
    bound_callback = rng_cog.flip_coin.callback.__get__(rng_cog, type(rng_cog))
    await bound_callback(interaction, None)
    called_with = interaction.response.send_message.call_args[0][0]

    # Need exactly these strings otherwise it picks up Heads and Tails
    # from the "Flipping a coin between: _{sides_formatted}_"
    assert "**Heads**!" in called_with or "**Tails**!" in called_with


@pytest.mark.asyncio
async def test_flip_coin_custom():
    bot = MagicMock()
    interaction = AsyncMock(spec=Interaction)
    interaction.response = AsyncMock()
    interaction.response.send_message = AsyncMock()

    rng_cog = rng.RNG(bot)
    bound_callback = rng_cog.flip_coin.callback.__get__(rng_cog, type(rng_cog))

    args = "One Two"
    await bound_callback(interaction, args)
    called_with = interaction.response.send_message.call_args[0][0]

    # Need exactly these strings otherwise it picks up Heads and Tails
    # from the "Flipping a coin between: _{sides_formatted}_"
    args_list = args.split(" ")
    formatted_args = [f"**{arg}**!" for arg in args_list]

    assert any(result in called_with for result in formatted_args)


@pytest.mark.asyncio
async def test_flip_coin_custom_with_five_args():
    bot = MagicMock()
    interaction = AsyncMock(spec=Interaction)
    interaction.response = AsyncMock()
    interaction.response.send_message = AsyncMock()

    rng_cog = rng.RNG(bot)
    bound_callback = rng_cog.flip_coin.callback.__get__(rng_cog, type(rng_cog))

    args = "One Two Three Four Five"
    await bound_callback(interaction, args)
    called_with = interaction.response.send_message.call_args[0][0]

    # Need exactly these strings otherwise it picks up Heads and Tails
    # from the "Flipping a coin between: _{sides_formatted}_"
    args_list = args.split(" ")
    formatted_args = [f"**{arg}**!" for arg in args_list]

    assert any(result in called_with for result in formatted_args)


@pytest.mark.asyncio
async def test_flip_coin_custom_one_option():
    bot = MagicMock()
    interaction = AsyncMock(spec=Interaction)
    interaction.response = AsyncMock()
    interaction.response.send_message = AsyncMock()

    rng_cog = rng.RNG(bot)
    bound_callback = rng_cog.flip_coin.callback.__get__(rng_cog, type(rng_cog))

    args = "One"
    await bound_callback(interaction, args)
    called_with = interaction.response.send_message.call_args[0][0]

    assert "two or more" in called_with


@pytest.mark.asyncio
async def test_flip_coin_fixed_random(mocker):
    bot = MagicMock()
    interaction = AsyncMock(spec=Interaction)
    interaction.response = AsyncMock()
    interaction.response.send_message = AsyncMock()
    mocker.patch("random.choice", return_value="Heads")

    rng_cog = rng.RNG(bot)
    bound_callback = rng_cog.flip_coin.callback.__get__(rng_cog, type(rng_cog))
    await bound_callback(interaction, None)
    called_message = interaction.response.send_message.call_args[0][0]
    assert "**Heads**!" in called_message


# 1. For the RNG Cog (`test_rng.py`):
# @pytest.mark.asyncio
# async def test_flip_coin_custom():
#     """Test coin flip with custom options"""
#     interaction = AsyncMock(spec=Interaction)
#     cog = rng_cog()
#
#     await cog.flip_coin(interaction, "Red Blue")
#
#     called_with = interaction.response.send_message.call_args[0][0]
#     assert any(result in called_with for result in ["Red!", "Blue!"])
#
# @pytest.mark.asyncio
# async def test_flip_coin_single_option():
#     """Test coin flip with single option (edge case)"""
#     interaction = AsyncMock(spec=Interaction)
#     cog = rng_cog()
#
#     await cog.flip_coin(interaction, "Single")
#
#     called_with = interaction.response.send_message.call_args[0][0]
#     assert "Single!" in called_with
# ```
#
# 2. For the Stock Cog (`test_stock.py`), add more edge cases:
# ```python
# @pytest.mark.asyncio
# async def test_get_stock_price_no_price(mocker):
#     """Test behavior when no price is found"""
#     async def fake_fetch(url: str) -> BeautifulSoup:
#         html = "<html><body>No price information</body></html>"
#         return BeautifulSoup(html, "html.parser")
#
#     mocker.patch("cogs.stock.fetch_page_contents", fake_fetch)
#     result = await stock.get_stock_price("https://testing.com")
#     assert result == "Price not found"
#
# @pytest.mark.asyncio
# async def test_add_watching_invalid_url(mocker):
#     """Test adding an invalid URL"""
#     bot = MagicMock()
#     interaction = AsyncMock(spec=Interaction)
#     stock_cog = stock.Stock(bot)
#
#     mocker.patch("cogs.stock.get_stock_name", return_value=None)
#
#     bound_callback = stock_cog.add_watching.callback.__get__(stock_cog, type(stock_cog))
#     await bound_callback(interaction, "invalid_url")
#
#     interaction.response.send_message.assert_called_with(
#         "Could not get the product name. Please provide a name manually",
#         ephemeral=True
#     )
#
# @pytest.mark.asyncio
# async def test_auto_check_stock(mocker):
#     """Test the automatic stock checking functionality"""
#     bot = MagicMock()
#     mock_stock = MagicMock(
#         user_id=123,
#         stock_url="https://test.com",
#         stock_name="Test Product",
#         stock_status=0,
#         last_checked="2024-01-01",
#         check_interval=1,
#         price="$99.99"
#     )
#
#     mocker.patch("cogs.stock.get_all_watched", return_value=[mock_stock])
#     mocker.patch("cogs.stock.check_stock", return_value=1)
#     mocker.patch("cogs.stock.get_stock_price", return_value="$89.99")
#     mocker.patch("asyncio.sleep", return_value=None)
#
#     await stock.auto_check_stock(bot, interval=1)
#
#     # Verify user was notified of changes
#     bot.fetch_user.assert_called_once_with(123)
# ```
#
# 3. For database utilities (`test_db.py`), add more complex scenarios:
# ```python
# def test_concurrent_stock_updates(test_db, sample_user_stock):
#     """Test handling multiple updates to the same stock"""
#     test_db.add(sample_user_stock)
#     test_db.commit()
#
#     # Simulate concurrent price updates
#     session1 = test_db
#     session2 = test_db
#
#     stock1 = session1.query(User_Stock).filter_by(
#         user_id=sample_user_stock.user_id
#     ).first()
#     stock2 = session2.query(User_Stock).filter_by(
#         user_id=sample_user_stock.user_id
#     ).first()
#
#     stock1.price = "$100.00"
#     stock2.price = "$110.00"
#
#     session1.commit()
#
#     # Should raise an error due to concurrent modification
#     with pytest.raises(Exception):
#         session2.commit()
#
# @pytest.mark.parametrize("invalid_data", [
#     {"user_id": None},
#     {"stock_url": ""},
#     {"stock_status": 999},
#     {"check_interval": -1},
# ])
# def test_invalid_stock_data(test_db, sample_user_stock, invalid_data):
#     """Test handling invalid data in User_Stock"""
#     for key, value in invalid_data.items():
#         setattr(sample_user_stock, key, value)
#
#     test_db.add(sample_user_stock)
#     with pytest.raises(Exception):
#         test_db.commit()
# ```
#
# 4. Add integration tests:
# ```python
# @pytest.mark.integration
# async def test_full_stock_workflow():
#     """Test the entire stock watching workflow"""
#     # Setup
#     bot = MagicMock()
#     user = MagicMock(id=123, name="TestUser")
#     url = "https://test.com/product"
#
#     # Add stock to watch
#     await stock.add_stock(user, url, "Test Product")
#
#     # Verify stock was added
#     watched_stocks = await stock.get_users_watched(user)
#     assert len(watched_stocks) == 1
#     assert watched_stocks[0].stock_url == url
#
#     # Simulate price change
#     old_price = watched_stocks[0].price
#     await stock.update_stock_price(watched_stocks[0], "$150.00")
#
#     # Verify price was updated
#     updated_stocks = await stock.get_users_watched(user)
#     assert updated_stocks[0].price != old_price
#     assert updated_stocks[0].price == "$150.00"
# ```
#
# 5. Add error handling tests:
# ```python
# @pytest.mark.asyncio
# async def test_error_handling():
#     """Test the error handling in commands"""
#     interaction = AsyncMock(spec=Interaction)
#     error = app_commands.AppCommandError()
#
#     cog = stock.Stock(MagicMock())
#     await cog.on_application_command_error(interaction, error)
#
#     interaction.response.send_message.assert_called_with(
#         "Command was unable to be executed",
#         ephemeral=True
#     )
# ```
