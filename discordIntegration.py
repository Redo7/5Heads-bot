from imports import *
from discord.app_commands import Choice
from typing import Optional
import datetime

async def send_dm(user_id, message):
    try:
        user = await bot.fetch_user(user_id)
        dm_channel = await user.create_dm()
        await dm_channel.send(message)
    except discord.HTTPException as e:
        print(f"Failed to send DM to: {e}")

async def send_embed(user_id, embed):
    try:
        user = await bot.fetch_user(user_id)
        dm_channel = await user.create_dm() 
        await dm_channel.send(embed=embed.build())
    except discord.HTTPException as e:
        print(f"Failed to send DM to: {e}")

@bot.hybrid_command(name="testembed", description="Test an embed")
@app_commands.choices(ephemeral=[
        Choice(name="Yes", value=1),
        Choice(name="No", value=0)
        ])
async def test_embed(ctx, ephemeral: Optional[Choice[int]], title=None, description=None, url=None, color=None, timestamp=None, author=None, author_url=None, author_avatar=None, thumbnail=None, image=None, footer=None, fields=None) -> None:
    embed = EmbedBuilder(title=title, description=description, url=url, color=color, timestamp=timestamp, author=author, author_url=author_url, author_avatar=author_avatar, thumbnail=thumbnail, image=image, footer=footer, fields=fields)
    await ctx.send(embed=embed.build()) if ephemeral == 0 else await ctx.send(embed=embed.build(), ephemeral=True)

class EmbedBuilder:
    def __init__(self, *, title=None, description=None, url=None, color=None, timestamp=None, author=None, author_url=None, author_avatar=None, thumbnail=None, image=None, footer=None, fields=None):
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
                self.embed.add_field(name=field.name, value=field.value, inline=field.inline)

    def build(self):
        return self.embed
