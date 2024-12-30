import os
import sys
import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice

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

@bot.hybrid_command(name="sync", description="Syncs commands", hidden=True)
async def sync(ctx):
    if str(ctx.author.id) == OWNER_ID:
        resp = await bot.tree.sync()
        msg = f"Syncing {len(resp)} commands."
        await ctx.send(msg)
        print(msg)
    else:
        await ctx.send('Nah uh')

@bot.hybrid_command(name="reload", description="Reloads a cog", hidden=True)
@app_commands.choices(name=[
        Choice(name="Admin", value="admin"),
        Choice(name="Config", value="config"),
        Choice(name="Discord Integration", value="discordIntegration"),
        Choice(name="Embed Builder", value="embedBuilder"),
        Choice(name="Misc", value="misc"),
        Choice(name="On_message", value="on_message"),
        Choice(name="Recruit", value="recruit"),
        Choice(name="Tenor", value="tenor")
        ])
async def reload(ctx, name: Choice[str],):
    try:
        await bot.unload_extension(f"cogs.{name.value}")
        await bot.load_extension(f"cogs.{name.value}")
        await ctx.send(f"{name.name} cog reloaded")
    except Exception as e: print(e)


async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            print(f"Loading {filename[:-3]} cog")
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    await load()  # Load the cogs
    await bot.start(TOKEN)

asyncio.run(main())
sys.stdout.reconfigure(encoding='utf-8')