from discord.ext import commands
import discord


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_join(member: discord.Member):
        print(f'{member.name} has joined the server.')

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        
        if "shit" in message.content.lower():
            await message.delete()
            await message.channel.send(f"{message.author.mention}, please refrain from using inappropriate language.")
        
        #await self.bot.process_commands(message)


async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
