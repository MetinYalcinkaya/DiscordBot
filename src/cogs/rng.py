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

    # @commands.group(name="rng")
    # async def rng(self, ctx):
    #     if ctx.invoked_subcommand is None:
    #         subcommand_names = ", ".join(
    #             [cmd.name for cmd in ctx.command.commands if cmd.name != "test"]
    #         )
    #         await ctx.reply(f"Available commands: **{subcommand_names}**")

    # @commands.group(name="flip")
    # async def flip(self, ctx):
    #     if ctx.invoked_subcommand is None:
    #         subcommand_names = ", ".join(
    #             [cmd.name for cmd in ctx.command.commands if cmd.name != "test"]
    #         )
    #         await ctx.reply(f"Available subcommands: **{subcommand_names}**")

    # @rng.group(name="roll")
    # async def roll(self, ctx):
    #     if ctx.invoked_subcommand is None:
    #         subcommand_names = ", ".join(
    #             [cmd.name for cmd in ctx.command.commands if cmd.name != "test"]
    #         )
    #         await ctx.reply(f"Available subcommands: **{subcommand_names}**")

    @rng.command(
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
        arg_sides = []
        if arguments:
            arg_sides = arguments.split(" ")

        if len(arg_sides) == 0:
            SIDES = ["Heads", "Tails"]
            sides_formatted = ", ".join([side for side in SIDES])
            message = f"Flipping a coin between: {sides_formatted}...\n\n{random.choice(SIDES)}!"
            await interaction.response.send_message(message)
        else:
            sides_formatted = ", ".join([arg for arg in arg_sides])
            message = f"Flipping a coin between: {sides_formatted}...\n\n{random.choice(arg_sides)}!"
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
