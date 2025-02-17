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
