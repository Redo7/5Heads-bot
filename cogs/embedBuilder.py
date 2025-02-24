import os
import discord
from discord import app_commands
from discord.ext import commands
import datetime

OWNER_ID = os.getenv('OWNER_ID')
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', owner_id=OWNER_ID, intents=intents)

class embedBuilder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ready = False
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.ready = True
        print(f"Embed builder cog loaded")

    def embed(self, *, title=None, description=None, url=None, color=None, timestamp=None, author=None, author_url=None, author_avatar=None, thumbnail=None, image=None, footer=None, fields=None):
        if color != None:
            color = int(color)
        if timestamp != None:
            timestamp = datetime.datetime.fromisoformat(timestamp)
        self.embed = discord.Embed(title=title, description=description, url=url, color=color, timestamp=timestamp)
        self.embed.set_author(name=author, url=author_url, icon_url=author_avatar)
        self.embed.set_thumbnail(url=thumbnail)
        self.embed.set_image(url=image)
        self.embed.set_footer(text=footer)
        if fields:
            for field in fields:
                self.embed.add_field(name=field["name"], value=field["value"], inline=field["inline"])
        return self.embed

    def build(self):
        return self.embed
    
async def setup(bot):
    await bot.add_cog(embedBuilder(bot))