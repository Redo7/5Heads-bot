import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice

import os
from dotenv import find_dotenv, load_dotenv
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
TOKEN = os.getenv('TOKEN')
intents = discord.Intents.default()
intents.message_content = True
OWNER_ID = int(os.getenv('OWNER_ID'))
bot = commands.Bot(command_prefix='!', owner_id=OWNER_ID, intents=intents)

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.owner_id = int(os.getenv('OWNER_ID'))

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Admin cog loaded")

    @bot.hybrid_command(name="sync", description="Syncs commands", hidden=True)
    async def sync(self, ctx):
        if ctx.author.id == OWNER_ID:
            resp = await self.bot.tree.sync()   
            msg = f"Syncing {len(resp)} commands."  
            await ctx.send(msg) 
            print(msg)  
        else:
            await ctx.send("Nah uh")

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
    async def reload(self, ctx, name: Choice[str],):
        try:
            await self.bot.unload_extension(f"cogs.{name.value}")
            await self.bot.load_extension(f"cogs.{name.value}")
            msg = f"{name.name} cog reloaded"
            await ctx.send(msg)
            print(msg)
        except Exception as e: print(e)

    @commands.has_permissions(manage_messages=True)
    @bot.hybrid_command(name='purge', brief='Deletes a specified number of messages from the current channel')
    async def purge(self, ctx, amount: int):
        await ctx.send(f'Purging messages...')
        deleted = await ctx.channel.purge(limit=amount)
        if len(deleted) == 0:
            embed = discord.Embed(title='Purge "complete"', color=0xED1B53)
            embed.description = 'No messages were deleted (bruh)'
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title='Purge complete', color=0x75FF81)
            embed.description = f'{len(deleted)} messages were deleted'
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Admin(bot))