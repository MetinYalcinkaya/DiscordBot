import random

from discord.ext import commands

from config import MY_USER_ID


class RNG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="rng")
    async def rng(self, ctx):
        if ctx.invoked_subcommand is None:
            subcommand_names = ", ".join(
                [cmd.name for cmd in ctx.command.commands if cmd.name != "test"]
            )
            await ctx.reply(f"Available commands: **{subcommand_names}**")

    @commands.group(name="flip")
    async def flip(self, ctx):
        if ctx.invoked_subcommand is None:
            subcommand_names = ", ".join(
                [cmd.name for cmd in ctx.command.commands if cmd.name != "test"]
            )
            await ctx.reply(f"Available subcommands: **{subcommand_names}**")

    @commands.group(name="roll")
    async def roll(self, ctx):
        if ctx.invoked_subcommand is None:
            subcommand_names = ", ".join(
                [cmd.name for cmd in ctx.command.commands if cmd.name != "test"]
            )
            await ctx.reply(f"Available subcommands: **{subcommand_names}**")

    @flip.command(name="coin")
    async def flip_coin(self, ctx, *args):
        random.seed()
        if len(args) == 0:
            SIDES = ["Heads", "Tails"]
            await ctx.reply(f"{random.choice(SIDES)}!")
        else:
            await ctx.reply(f"{random.choice(args)}!")

    @roll.command(name="dice")
    async def roll_dice(self, ctx, *args):
        print("Dice")

    @rng.command(name="help")
    async def help(self, ctx):
        await ctx.reply("")

    @rng.command(name="test")
    async def test(self, ctx):
        print("Attempting to execute test function")
        if ctx.author.id == MY_USER_ID:
            print(f"Authorised user: {ctx.author.name} - ID: {ctx.author.id}")
            print("\n\n--------------- Testing ---------------\n\n")

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            await ctx.respond("You don't have permission to use that command")
        else:
            raise error  # raises the other errors


async def setup(bot):
    await bot.add_cog(RNG(bot))
