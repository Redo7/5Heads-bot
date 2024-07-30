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

@bot.hybrid_command(name="widepeepohappy", description="Sends a widepeepoHappy emote")
async def widepeepohappy(ctx: commands.Context) -> None:
    await ctx.send('<:WidePeepoHappy1:768481090079686677><:WidePeepoHappy2:768481089936818216><:WidePeepoHappy3:768481090029355038><:WidePeepoHappy4:768481090041413653>')

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
            new_msg = await message.channel.send(message.content.replace(link, "https://fxtwitter.com"))
            
            await new_msg.add_reaction('✔️')
            await new_msg.add_reaction('✖️')

            def check(reaction, user):
                return user == message.author and str(reaction.emoji) == '✔️'
            
            try:
                reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
            except asyncio.TimeoutError:
                await new_msg.delete()
            else:
                await new_msg.clear_reactions()
