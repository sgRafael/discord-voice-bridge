
from discord.ext import commands
import sys
import os
from config.api import APIConfig
import aiohttp

class System(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="hello", aliases=["hey"])
    async def hello(self, ctx: commands.Context, arg: str = None):
        await ctx.send(f'Hello {ctx.author.mention}!')

    @commands.command(name="reboot", aliases=["reload", "restart"])
    @commands.is_owner()  # Just the bot owner can use this command
    async def reboot(self, ctx: commands.Context):
        await ctx.send("🔄 Reiniciando...")
        os.execv(sys.executable, ['python'] + sys.argv)


async def setup(bot: commands.Bot):
    await bot.add_cog(System(bot))


