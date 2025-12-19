import os
from discord.ext import commands
import logging

from config import DISCORD_TOKEN, CANAL_JARVIS, COMMAND_PREFIX, INTENTS, DISCORD_LOG_PATH
from services.control import ControlClient
from config.api import APIConfig

bot = commands.Bot(
    command_prefix=COMMAND_PREFIX,
    intents=INTENTS
)

handler = logging.FileHandler(filename=DISCORD_LOG_PATH, encoding='utf-8', mode='w')

def main():    
    @bot.event
    async def on_ready():
        for filename in os.listdir('src/cogs'):
            if filename.endswith('.py') and not filename.startswith('_'):
                await bot.load_extension(f'cogs.{filename[:-3]}')

        bot.control = ControlClient(
            url=APIConfig.CONTROL,
            token=DISCORD_TOKEN,
            session_id='discord.bot',
        )
        await bot.control.connect()
        
        print(f'Logged in as {bot.user.name} - {bot.user.id}')
        print('------')
        
        canal = bot.get_channel(CANAL_JARVIS)
        if canal:
            await canal.send("✅ Bot iniciado y listo.")

    
    #bot.run(DISCORD_TOKEN, log_handler=handler, log_level=logging.DEBUG)
    bot.run(DISCORD_TOKEN, log_level=logging.DEBUG)


if __name__ == "__main__":
    main()


