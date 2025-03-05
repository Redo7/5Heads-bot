import discord
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

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.owner_id = int(os.getenv('OWNER_ID'))

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Admin cog loaded")

    @bot.hybrid_command(name="sync", description="Syncs commands", hidden=True)
    async def sync(self, ctx):
        if ctx.author.id != OWNER_ID:
            await ctx.send("Nah uh")
            return
        resp = await self.bot.tree.sync()   
        msg = f"Syncing {len(resp)} commands."  
        await ctx.send(msg) 
        print(msg)

    @commands.has_permissions(manage_messages=True)
    @bot.hybrid_command(name='purge', description='Deletes a specified number of messages from the current channel')
    @app_commands.describe(amount="The amount of messages to delete")
    async def purge(self, ctx, amount: int):
        await ctx.send(f'Purging messages...')
        deleted = await ctx.channel.purge(limit=amount+1)
        if len(deleted) == 0:
            embed = embedBuilder(self.bot).embed(
                color = "#ED1B53",
                title = 'Purge "complete"',
                description = 'No messages were deleted (bruh)'
                )
            await ctx.send(embed=embed)
        else:
            embed = embedBuilder(self.bot).embed(
                color = "#75FF81",
                title = 'Purge complete',
                description = f'{len(deleted)} messages were deleted'
                )
            await ctx.send(embed=embed)

    @commands.has_permissions(manage_messages=True)
    @commands.hybrid_command(name="safepurge", description="Reply to a message to delete everything after it")
    async def safe_purge(self, ctx):
        if ctx.interaction is not None:
            await ctx.send("This command must be invoked with `!safepurge`")
            return
        if ctx.message.reference:
            try:
                reply_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            except discord.NotFound:
                await ctx.send("Could not find the message.")
                return

            count = 0
            async for message in ctx.channel.history(limit=None, after=reply_message):
                count += 1
            await self.purge(ctx, count + 1)
        else:
            await ctx.send("This command must be used as a reply to a message.")

async def setup(bot):
    await bot.add_cog(Admin(bot))