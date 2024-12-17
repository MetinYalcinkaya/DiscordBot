from discord.ext import commands


class CoinFlip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="flip")
    async def flip_coin(self, ctx):
        await ctx.reply("Hello, world!")


def setup(bot):
    bot.add_cog(CoinFlip(bot))
