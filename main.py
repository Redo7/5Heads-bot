import os
import sys
import asyncio
import discord
import traceback
import datetime
from discord import app_commands
from discord.ext import commands
from cogs.embedBuilder import embedBuilder
from cogs.discordIntegration import *

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
    if os.getenv('TOKEN') == os.getenv('DEV'): return
    embed = embedBuilder(bot).embed(
            color=0x75FF81,
            author=bot.user,
            author_avatar=bot.user.avatar,
            description=f"**Bot is online**",
            timestamp=f"{datetime.datetime.now().isoformat()}"
        )
    await discordIntegration(bot).send_embed(OWNER_ID, embed)

async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            print(f"Loading {filename[:-3]} cog")
            await bot.load_extension(f"cogs.{filename[:-3]}")

@bot.event
async def on_command_error(ctx: commands.Context, error):
    traceback_str = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
    if isinstance(error, commands.CommandNotFound):
        title = "Command not found. Please check the command and try again."
    elif isinstance(error, commands.MissingRequiredArgument):
        title = "Missing required argument. Please check the command usage."
    elif isinstance(error, commands.BadArgument):
        title = "Invalid argument. Please check the command usage."
    elif isinstance(error, commands.CommandInvokeError):
        # Send the error and traceback
        title = "An error occurred while executing the command."
        print(traceback_str)
    else:
        title = "An unexpected error occurred."
        print(traceback_str)
    embed = embedBuilder(bot).embed(
                color=0xed1b53,
                author=title,
                author_avatar=bot.user.avatar,
                description=f"```py\n{error}\n```",
                timestamp=f"{datetime.datetime.now().isoformat()}"
            )
    await ctx.send(embed=embed, ephemeral=True)

async def main():
    bot.remove_command("help")
    await load()  # Load the cogs
    await bot.start(TOKEN)

asyncio.run(main())
sys.stdout.reconfigure(encoding='utf-8')