from imports import *
import random
from config import config
from discord.app_commands import Choice

# set the apikey and limit
apikey = TENOR_API_KEY  # click to set to your apikey
ckey = CLIENT_KEY  # set the client_key for the integration and use the same value for all API calls

@bot.hybrid_command(name="gifs", description="Send a gif targeted at someone")
@app_commands.choices(name=[
    Choice(name="Cheer", value="cheer"),
    Choice(name="Clap", value="clap"),
    Choice(name="Confused", value="confused"),
    Choice(name="High Five", value="high five"),
    Choice(name="Homie Kiss", value="homie kiss"),
    Choice(name="Hug", value="hug"),
    Choice(name="Kick", value="kick"),
    Choice(name="Kiss", value="kiss"),
    Choice(name="Kys?", value="kys"),
    Choice(name="Peek", value="peek"),
    Choice(name="Sad", value="sad"),
    Choice(name="Slap", value="slap"),
    Choice(name="Wave", value="wave")
    ])
@app_commands.choices(anime=[
        Choice(name="Yes", value=1),
        Choice(name="No", value=0)
        ])
async def gifs(
    ctx: commands.Context, 
    name: Choice[str], 
    anime: Choice[int],
    target: str = commands.parameter(description="The @ of the person the gif is targetted at"),
    ) -> None:

    resp = {
        'cheer': 'cheers for',
        'clap': 'claps for',
        'confused': 'is confused about',
        'high five': 'high fives',
        'homie kiss': 'homie kisses',
        'hug': 'hugs',
        'kick': 'kicks',
        'kiss': 'kisses',
        'kys': '',
        'peek': 'peeks at',
        'sad': 'is sad for',
        'slap': 'slaps',
        'wave': 'waves at'
    }

    if name.value == 'kys' and random.randint(0, 1) == 1:
        await ctx.send(f"{target}... You should kill yourself ***NOW***")
        await ctx.send("https://c.tenor.com/sAhYu4Wd7IcAAAAC/tenor.gif")
        return
    elif name.value == 'kys' and random.randint(0, 1) == 0:
        await ctx.send(f"{target}... Keep yourself safe :grin:")
        await ctx.send("https://c.tenor.com/isav-uIsV64AAAAC/tenor.gif")
        return
    else:
        pass

    lmt = 8 # amount of gifs to retrieve
    # get the top 8 GIFs for the search term
    if anime.value == 1:
        r = requests.get(
            "https://tenor.googleapis.com/v2/search?q=%s+anime&key=%s&client_key=%s&limit=%s" % (name.value, apikey, ckey,  lmt))
    else:
        r = requests.get(
            "https://tenor.googleapis.com/v2/search?q=%s&key=%s&client_key=%s&limit=%s" % (name.value, apikey, ckey,  lmt))
        
    if r.status_code == 200:
        # load the GIFs using the urls for the smaller GIF sizes
        gifs = json.loads(r.content)
        await ctx.send(f"{ctx.author.display_name} {resp[name.value]} {target}")
        await ctx.send(gifs['results'][random.randint(0, 7)]['url'])
    else:
        gifs = None
        await ctx.send("Couldn't retrieve gifs")