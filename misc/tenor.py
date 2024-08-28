from imports import *
import random
from config import config
from discord.app_commands import Choice
from typing import Optional

apikey = TENOR_API_KEY  
ckey = CLIENT_KEY

@bot.hybrid_command(name="gifs", description="Send a gif targeted at someone")
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
async def gifs(
    ctx: commands.Context, 
    name: Choice[str], 
    anime: Optional[Choice[int]],
    target: str = commands.parameter(description="The @ of the person the gif is targetted at")
    ) -> None:

    resp = {
        'bonk': f'bonks {target}',
        'chase': f'runs after {target}',
        'cheer': f'cheers for {target}',
        'clap': f'claps for {target}',
        'confused': f'is confused about {target}',
        'cover someone elses mouth': f"covers {target}'s mouth",
        'high five': f'high fives {target}',
        'homie kiss': f'homie kisses {target}',
        'hug': f'hugs {target}',
        'kick': f'kicks {target}',
        'kiss': f'kisses {target}',
        'kys': '',
        'peek': f'peeks at {target}',
        'throw someone': f'yeets {target}',
        'sad': f'is sad for {target}',
        'slapping': f'slaps {target}',
        'slapping competition': f'slaps {target}',
        'spit': f'spits on {target}',
        'wave': f'waves at {target}'
    }

    kysRandInt = random.randint(0, 1)
    if name.value == 'kys' and kysRandInt == 1:
        await ctx.send(f"{target}... You should kill yourself ***NOW***")
        await ctx.send("https://c.tenor.com/sAhYu4Wd7IcAAAAC/tenor.gif")
        return
    elif name.value == 'kys' and kysRandInt == 0:
        await ctx.send(f"{target}... Keep yourself safe :grin:")
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