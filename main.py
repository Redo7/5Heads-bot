import os
import sys
import asyncio
import discord
from discord import app_commands
from discord.ext import commands

from dotenv import find_dotenv, load_dotenv
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
TOKEN = os.getenv('TOKEN')
OWNER_ID = os.getenv('OWNER_ID')
RECRUIT_CHANNEL = int(os.getenv('RECRUIT_CHANNEL'))
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', owner_id=OWNER_ID, intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            print(f"Loading {filename[:-3]} cog")
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    bot.remove_command("help")
    await load()  # Load the cogs
    await bot.start(TOKEN)

asyncio.run(main())
sys.stdout.reconfigure(encoding='utf-8')