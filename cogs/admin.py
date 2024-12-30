import discord
from discord import app_commands
from discord.ext import commands

import os
TOKEN = os.getenv('TOKEN')
OWNER_ID = os.getenv('OWNER_ID')
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', owner_id=OWNER_ID, intents=intents)

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Admin cog loaded")

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