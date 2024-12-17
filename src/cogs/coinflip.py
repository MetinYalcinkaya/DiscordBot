from discord.ext import commands


class CoinFlip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="flip")
    async def flip(self, ctx):
        if ctx.invoked_subcommand is None:
            subcommand_names = ", ".join([cmd.name for cmd in ctx.command.commands])
            await ctx.send(f"Available subcommands: {subcommand_names}")

    @flip.command(name="coin")
    async def flip_coin(self, ctx):
        await ctx.reply("Hello, world!")


def setup(bot):
    bot.add_cog(CoinFlip(bot))
