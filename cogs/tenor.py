import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice

import os
import json
import random
import requests
from cogs import config
from typing import Optional
from dotenv import find_dotenv, load_dotenv

intents = discord.Intents.default()
intents.message_content = True
OWNER_ID = os.getenv('OWNER_ID')
bot = commands.Bot(command_prefix='!', owner_id=OWNER_ID, intents=intents)

apikey = os.getenv('TENOR_API_KEY')
ckey = os.getenv('CLIENT_KEY')


class Tenor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Tenor cog loaded")

    @bot.hybrid_command(name="gifs", description="Send a gif targeted at someone")
    @app_commands.describe(name="The name of the action")
    @app_commands.describe(anime="Should the result be from an anime?")
    @app_commands.describe(target="The person to @ when the bot sends the gif")
    @app_commands.choices(name=[
        Choice(name="Bonk", value="bonk"),
        Choice(name="Chase", value="chase"),
        Choice(name="Cheer", value="cheer"),
        Choice(name="Clap", value="clap"),
        Choice(name="Confused", value="confused"),
        Choice(name="Cover Mouth", value="cover someone elses mouth"),
        Choice(name="High Five", value="high five"),
        Choice(name="Homie Kiss", value="homie kiss"),
        Choice(name="Hug", value="hug"),
        Choice(name="Kick", value="kick"),
        Choice(name="Kiss", value="kiss"),
        Choice(name="Kys?", value="kys"),
        Choice(name="Peek", value="peek"),
        Choice(name="Throw", value="throw someone"),
        Choice(name="Sad", value="sad"),
        Choice(name="Slap", value="slapping"),
        Choice(name="Slap (Competition)", value="slapping competition"),
        Choice(name="Spit", value="spit"),
        Choice(name="Wave", value="wave")
        ])
    @app_commands.choices(anime=[
            Choice(name="Yes", value=1),
            Choice(name="No", value=0)
            ])
    async def gifs(self,
        ctx: commands.Context, 
        name: Choice[str], 
        anime: Optional[Choice[int]],
        target: discord.User = commands.parameter(description="The @ of the person the gif is targetted at")
        ) -> None:

        resp = {
            'bonk': f'bonks {target.mention}',
            'chase': f'runs after {target.mention}',
            'cheer': f'cheers for {target.mention}',
            'clap': f'claps for {target.mention}',
            'confused': f'is confused about {target.mention}',
            'cover someone elses mouth': f"covers {target.mention}'s mouth",
            'high five': f'high fives {target.mention}',
            'homie kiss': f'homie kisses {target.mention}',
            'hug': f'hugs {target.mention}',
            'kick': f'kicks {target.mention}',
            'kiss': f'kisses {target.mention}',
            'kys': '',
            'peek': f'peeks at {target.mention}',
            'throw someone': f'yeets {target.mention}',
            'sad': f'is sad for {target.mention}',
            'slapping': f'slaps {target.mention}',
            'slapping competition': f'slaps {target.mention}',
            'spit': f'spits on {target.mention}',
            'wave': f'waves at {target.mention}'
        }

        kysRandInt = random.randint(0, 1)
        if name.value == 'kys' and kysRandInt == 1:
            await ctx.send(f"{target.mention}... You should kill yourself ***NOW***")
            await ctx.send("https://c.tenor.com/sAhYu4Wd7IcAAAAC/tenor.gif")
            return
        elif name.value == 'kys' and kysRandInt == 0:
            await ctx.send(f"{target.mention}... Keep yourself safe :grin:")
            await ctx.send("https://c.tenor.com/isav-uIsV64AAAAC/tenor.gif")
            return
        else:
            pass

        lmt = 8 # amount of gifs to retrieve
        if anime is not None and anime.value == 1:
            r = requests.get(
                "https://tenor.googleapis.com/v2/search?q=%s+anime&key=%s&client_key=%s&limit=%s" % (name.value, apikey, ckey,  lmt))
        else:
            r = requests.get(
                "https://tenor.googleapis.com/v2/search?q=%s&key=%s&client_key=%s&limit=%s" % (name.value, apikey, ckey,  lmt))
            
        if r.status_code == 200:
            gifs = json.loads(r.content)
            await ctx.send(f"{ctx.author.display_name} {resp[name.value]}")
            await ctx.send(gifs['results'][random.randint(0, 7)]['url'])
        else:
            gifs = None
            await ctx.send("Couldn't retrieve gifs")

async def setup(bot):
    await bot.add_cog(Tenor(bot))