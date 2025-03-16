import discord
import datetime
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice
from cogs.embedBuilder import embedBuilder

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

    @commands.hybrid_group(name="owner", description="Owner commands")
    @commands.is_owner()
    async def owner(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Please specify a subcommand.")

    @owner.command(name="sync", description="Syncs commands", hidden=True)
    @commands.is_owner()
    async def sync(self, ctx):
        resp = await self.bot.tree.sync()   
        msg = f"Syncing {len(resp)} commands."  
        await ctx.send(msg) 
        print(msg)

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

    @owner.command(name="reload", description="Reloads a cog", hidden=True)
    @app_commands.describe(name="The cog to reload")
    @app_commands.choices(name=choices)
    @commands.is_owner()
    async def reload(self, ctx, name: Choice[str],):
        try:
            await self.bot.reload_extension(f"cogs.{name.value}")
            msg = f"{name.name} cog reloaded"
            await ctx.send(msg)
            print(msg)
        except Exception as e:
            await ctx.send(e, ephemeral=True)
            print(e)

    @owner.command(name="load", description="Reloads a cog", hidden=True)
    @app_commands.describe(name="The cog to load")
    @app_commands.choices(name=choices)
    @commands.is_owner()
    async def load(self, ctx, name: Choice[str],):
        try:
            await self.bot.load_extension(f"cogs.{name.value}")
            msg = f"{name.name} cog loaded"
            await ctx.send(msg)
            print(msg)
        except Exception as e:
            await ctx.send(e, ephemeral=True)
            print(e)

    @owner.command(name="unload", description="Unloads a cog", hidden=True)
    @app_commands.describe(name="The cog to unload")
    @app_commands.choices(name=choices)
    @commands.is_owner()
    async def unload(self, ctx, name: Choice[str],):
        try:
            await self.bot.unload_extension(f"cogs.{name.value}")
            msg = f"{name.name} cog unloaded"
            await ctx.send(msg)
            print(msg)
        except Exception as e:
            await ctx.send(e, ephemeral=True)
            print(e)

    @owner.command(name="context", description="Log message context")
    async def context_misc(self, ctx: commands.Context) -> None:
        context = ""
        for var, val in vars(ctx).items():
            context += f"{var}: {val}\n"

        embed = embedBuilder(bot).embed(
                color="#ffd330",
                author="Context",
                author_avatar=self.bot.user.avatar,
                description=f"```py\n{context}\n```",
                timestamp=f"{datetime.datetime.now().timestamp()}"
            )
        await ctx.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Cogs(bot))
