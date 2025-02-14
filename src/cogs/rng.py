import random
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from config import MY_USER_ID


class RNG(commands.Cog, name="Random Number Functionality"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    rng = app_commands.Group(
        name="rng", description="Collection of random number generation tools"
    )

    @app_commands.command(
        name="flip_coin",
        description="Flip a coin with given arguments or between heads and tails",
    )
    @app_commands.describe(
        arguments="Optional arguments that flips a coin between given values, separated by a space"
    )
    async def flip_coin(
        self, interaction: discord.Interaction, arguments: Optional[str]
    ):
        random.seed()
        sides_formatted = ""
        message = ""
        sides = ["Heads", "Tails"]

        if arguments:
            sides = []
            sides = arguments.split(" ")
            if len(sides) < 2:
                message = "You need two or more options!"
                await interaction.response.send_message(message)
                return

        sides_formatted = ", ".join([side for side in sides])
        message = f"Flipping a coin between: _{sides_formatted}_...\n\n**{random.choice(sides)}**!"
        await interaction.response.send_message(message)

    # @rng.command(name="dice")
    # async def roll_dice(self, ctx, *args):
    #     print("Dice")
    #
    # @rng.command(name="help")
    # async def help(self, ctx):
    #     await ctx.reply("")

    # @rng.command(name="test")
    # async def test(self, ctx):
    #     print("Attempting to execute test function")
    #     if ctx.author.id == MY_USER_ID:
    #         print(f"Authorised user: {ctx.author.name} - ID: {ctx.author.id}")
    #         print("\n\n--------------- Testing ---------------\n\n")

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


async def setup(bot):
    await bot.add_cog(RNG(bot))
