import discord
from discord.ext import commands
import datetime

class EmbedBuilder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Cog loaded")

    def build(self):
        return self.embed
    
async def setup(bot):
    await bot.add_cog(EmbedBuilder(bot))