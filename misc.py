from imports import *
from config import config
class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

@bot.hybrid_command(name="test", description="Log message context")
async def test(ctx: commands.Context) -> None:
    print(vars(ctx))
    await ctx.send("Done")

@bot.event
async def on_message(message):
    animation_3c = [':OC====3', ':C====3', '¦C===3', ':C==3', ':C=3', ':C3',
                    '¦3', ':3', '¦3', ':C3', ':C=3', '¦C3', ':C=3', ':C3', ':3']
    if ":3C====3" in message.content and message.author == bot.user:
        for frame in animation_3c:
            await message.edit(content=frame)
            time.sleep(0.4)

    if message.author == bot.user:
        return

    if ":3" in message.content and config.check_db(message.guild.id, 'animation_3c') == 1:
        await message.channel.send(":3C====3")

    twitter_links = ["https://x.com", "https://twitter.com"]
    for link in twitter_links:
        if message.content.startswith(link) and "/status/" in message.content and config.check_db(message.guild.id, 'twitter_links') == 1:
            await message.channel.send(message.content.replace(link, "https://fxtwitter.com"))
