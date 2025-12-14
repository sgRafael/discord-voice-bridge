from dotenv import load_dotenv
import os
import discord


load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL")

SERVER_SAMPLERATE = 24000


INTENTS = discord.Intents.default()
INTENTS.message_content = True
INTENTS.members = True
INTENTS.voice_states = True

COMMAND_PREFIX = "!"



CANAL_JARVIS = int(os.getenv("DEFAULT_TEXT_CHANNEL_ID"))


if not CANAL_JARVIS:
    raise RuntimeError("CANAL_JARVIS no definido")

if not DISCORD_TOKEN:
    raise RuntimeError("DISCORD_TOKEN no definido")

if not API_BASE_URL:
    raise RuntimeError("API_BASE_URL no definido")


DISCORD_LOG_PATH = "var/discord.log"

os.makedirs(os.path.dirname(DISCORD_LOG_PATH), exist_ok=True)
