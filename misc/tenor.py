from imports import *
import random
from config import config
from discord.app_commands import Choice

# set the apikey and limit
apikey = TENOR_API_KEY  # click to set to your apikey
ckey = CLIENT_KEY  # set the client_key for the integration and use the same value for all API calls

@bot.hybrid_command(name="gifs", description="Send a gif targeted at someone")
@app_commands.choices(choices=[
        Choice(name="Slap", value="slap"),
        Choice(name="Hug", value="hug")
        ])
async def gifs(ctx: commands.Context, choices: Choice[str], target: str = commands.parameter(description="The @ of the person the gif is targetted at")) -> None:
    lmt = 8 # amount of gifs to retrieve
    # get the top 8 GIFs for the search term
    r = requests.get(
        "https://tenor.googleapis.com/v2/search?q=%s&key=%s&client_key=%s&limit=%s" % (choices.value, apikey, ckey,  lmt))
    if r.status_code == 200:
        # load the GIFs using the urls for the smaller GIF sizes
        gifs = json.loads(r.content)
        await ctx.send(f"{ctx.author.global_name} {choices.value}s {target}")
        await ctx.send(gifs['results'][random.randint(0, 7)]['url'])
    else:
        gifs = None
        await ctx.send("Couldn't retrieve gifs")