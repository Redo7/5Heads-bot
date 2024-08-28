from imports import *
from config import config
import random

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

@bot.hybrid_command(name="context", description="Log message context")
async def context(ctx: commands.Context) -> None:
    print(vars(ctx))
    await ctx.send("Done")

@bot.hybrid_command(name="widepeepohappy", description="Sends a widepeepoHappy emote")
async def widepeepohappy(ctx: commands.Context) -> None:
    await ctx.send('<:WidePeepoHappy1:768481090079686677><:WidePeepoHappy2:768481089936818216><:WidePeepoHappy3:768481090029355038><:WidePeepoHappy4:768481090041413653>')

@bot.hybrid_command(name="8ball", description="Ask the Magic 8 Ball a question")
async def magic8ball(ctx: commands.Context, question: str) -> None:
    resp = [
        'It is certain',
        'It is decidedly so',
        'Without a doubt',
        'Yes definitely',
        'You may rely on it',
        'As I see it, yes',
        'Most likely',
        'Outlook good',
        'Yes',
        'Signs point to yes',
        'Reply hazy, try again',
        'Ask again later',
        'Better not tell you now',
        'Cannot predict now',
        'Concentrate and ask again',
        'Don’t count on it',
        'My reply is no',
        'My sources say no',
        'Outlook not so good',
        'Very doubtful'
    ]
    await ctx.send(f"*{ctx.author.display_name}* asks...\nQuestion: {question}\n*Answer:* **{resp[random.randint(0, 19)]}**")

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
        if link in message.content and "/status/" in message.content and config.check_db(message.guild.id, 'twitter_links') == 1:
            msg_split = message.content.split(' ')
            indices = [i for i, s in enumerate(msg_split) if link in s]
            new_msg = await message.channel.send(msg_split[indices[0]].replace(link, "https://fxtwitter.com"))
            
            await new_msg.add_reaction('✔️')
            await new_msg.add_reaction('✖️')

            def check(reaction, user):
                return user == message.author
            
            try:
                reaction, user = await bot.wait_for('reaction_add', timeout=10.0, check=check)
            except asyncio.TimeoutError:
                await new_msg.delete()
            else:
                if reaction.emoji == '✖️':
                    await new_msg.delete()
                elif reaction.emoji == '✔️':
                    await new_msg.clear_reactions()
                    
