import discord
from cogs.embedBuilder import embedBuilder
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice
from typing import Optional
import datetime

import os
OWNER_ID = os.getenv('OWNER_ID')
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', owner_id=OWNER_ID, intents=intents)

class discordIntegration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Discord integration cog loaded")

    async def send_dm(self, user_id, message):
        try:
            user = await self.bot.fetch_user(user_id)
            dm_channel = await user.create_dm()
            await dm_channel.send(message)
        except discord.HTTPException as e:
            print(f"Failed to send DM to: {e}")

    async def send_embed(self, user_id, embed):
        user = await self.bot.fetch_user(user_id)
        dm_channel = await user.create_dm() 
        await dm_channel.send(embed=embed)

    @bot.hybrid_command(name="testembed", description="Test an embed")
    @app_commands.choices(ephemeral=[
            Choice(name="Yes", value=1),
            Choice(name="No", value=0)
            ])
    async def test_embed(self, ctx, ephemeral: Optional[Choice[int]], title=None, description=None, url=None, color=None, timestamp=None, author=None, author_url=None, author_avatar=None, thumbnail=None, image=None, footer=None, fields=None) -> None:
        embed = embedBuilder(bot).embed(title=title, description=description, url=url, color=color, timestamp=timestamp, author=author, author_url=author_url, author_avatar=author_avatar, thumbnail=thumbnail, image=image, footer=footer, fields=fields)
        await ctx.send(embed=embed) if ephemeral != None and ephemeral.value == 0 else await ctx.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(discordIntegration(bot))