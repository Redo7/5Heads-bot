import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice

import os
from dotenv import find_dotenv, load_dotenv
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
intents = discord.Intents.default()
intents.message_content = True
OWNER_ID = int(os.getenv('OWNER_ID'))
bot = commands.Bot(command_prefix='!', owner_id=OWNER_ID, intents=intents)

class Cogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.owner_id = int(os.getenv('OWNER_ID'))

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Cog commands loaded")

    choices = [
        Choice(name="Admin", value="admin"),
        Choice(name="Config", value="config"),
        Choice(name="Discord Integration", value="discordIntegration"),
        Choice(name="Economy", value="economy"),
        Choice(name="Embed Builder", value="embedBuilder"),
        Choice(name="Gambling", value="gambling"),
        Choice(name="Misc", value="misc"),
        Choice(name="On_message", value="on_message"),
        Choice(name="Recruit", value="recruit"),
        Choice(name="Tenor", value="tenor")
        ]

    @bot.hybrid_command(name="reload", description="Reloads a cog", hidden=True)
    @app_commands.choices(name=choices)
    async def reload(self, ctx, name: Choice[str],):
        try:
            await self.bot.reload_extension(f"cogs.{name.value}")
            msg = f"{name.name} cog reloaded"
            await ctx.send(msg)
            print(msg)
        except Exception as e:
            await ctx.send(e, ephemeral=True)
            print(e)

    @bot.hybrid_command(name="load", description="Reloads a cog", hidden=True)
    @app_commands.choices(name=choices)
    async def load(self, ctx, name: Choice[str],):
        if ctx.author.id != OWNER_ID:
            await ctx.send("Nah uh")
            return
        try:
            await self.bot.load_extension(f"cogs.{name.value}")
            msg = f"{name.name} cog loaded"
            await ctx.send(msg)
            print(msg)
        except Exception as e:
            await ctx.send(e, ephemeral=True)
            print(e)

    @bot.hybrid_command(name="unload", description="Unloads a cog", hidden=True)
    @app_commands.choices(name=choices)
    async def unload(self, ctx, name: Choice[str],):
        if ctx.author.id != OWNER_ID:
            await ctx.send("Nah uh")
            return
        try:
            await self.bot.unload_extension(f"cogs.{name.value}")
            msg = f"{name.name} cog unloaded"
            await ctx.send(msg)
            print(msg)
        except Exception as e:
            await ctx.send(e, ephemeral=True)
            print(e)

async def setup(bot):
    await bot.add_cog(Cogs(bot))
