import logging
import discord
from discord.ext import commands
from config.api import APIConfig
import httpx
from contextlib import suppress
from utils.DiscordIO import DiscordIO


class Speech(commands.Cog):
    """Orquest audio between Discord and the coordinator."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.DiscordIO = DiscordIO()

    @commands.command(name="join", aliases=["connect"])
    async def join(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send("❌ Debes estar en un canal de voz.")
        await self.DiscordIO.connect(ctx.author.voice.channel)
        await ctx.send(f"🎧 Conectado a {ctx.author.voice.channel.name}")

    @commands.command(name="leave", aliases=["disconnect"]) 
    async def leave(self, ctx: commands.Context): 
        if not self.DiscordIO._connected:
            await ctx.send('❌ No estoy conectado.')
            return
        with suppress(Exception): 
            await self.DiscordIO.disconnect() 
        await ctx.send("👋 Desconectado.")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before: discord.VoiceState, after: discord.VoiceState):
        # was the bot moved?
        if not self.bot.user or member.id != self.bot.user.id:
            return

        if before.channel and not after.channel: # if left the channel
            await self.DiscordIO.disconnect()
            return
        
        if not before.channel and after.channel: # if joined the channel
            return
        
        if before.channel != after.channel: # if changed channel
            #await self.DiscordIO.connect(after.channel)
            return

    @commands.command(name="jarvis", aliases=["j"], help="Habla con Jarvis", description="Habla con Jarvis.", usage="!jarvis <mensaje>")
    async def jarvis(self, ctx: commands.Context, *, mensaje: str):
        sms = {"role": "user", "content": mensaje}
        payload = {"messages": [sms], "stream": True}
        msg = await ctx.send("🧠 Pensando...")
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                async with client.stream("POST", APIConfig.QUERY, json=payload) as response:
                    response.raise_for_status()

                    content = ""
                    async for chunk in response.aiter_text():
                        content = chunk
                        # Opcional: limitar la cantidad de ediciones para no saturar
                        if len(content) % 20 == 0:  # cada 20 caracteres
                            await msg.edit(content=content)

                    await msg.edit(content=content)  # mensaje final

        except Exception as e:
            await msg.edit(content=f"❌ Error: {type(e).__name__} - {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Speech(bot))

