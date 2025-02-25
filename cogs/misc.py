import time
import random
import asyncio
import datetime
import requests
from cogs import config
from cogs.embedBuilder import embedBuilder

import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice

import os
OWNER_ID = os.getenv('OWNER_ID')
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', owner_id=OWNER_ID, intents=intents)

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Misc cog loaded")

    @bot.hybrid_command(name="cooltext", description="Generate a text image from cooltext.com")
    @app_commands.choices(text_type=[
        Choice(name="Animated Glow", value="1"),
        Choice(name="Blinkie", value="2"),
        Choice(name="Burning", value="3"),
        Choice(name="Flaming", value="4"),
        Choice(name="Glitter", value="5"),
        Choice(name="Love", value="6"),
        Choice(name="Molten Core", value="7")
    ])
    async def cooltext(self, ctx, text_type: Choice[str], text):
        endpoints = {
            "Animated Glow": f"LogoID=26&Text={text}&FontSize=70&Color1_color=%23000000&Color2_color=%23FFFFFF&Color3_color=%23000000&Integer9=0&Integer13=on&Integer12=on&BackgroundColor_color=%23FFFFFF",
            "Blinkie": f"LogoID=819515844&Text={text}&FontSize=50&Color1_color=%23A34386&Integer1=25&Color2_color=%23FFFFFF&Integer9=0&Integer13=on&Integer12=on&BackgroundColor_color=%23000000",
            "Burning": f"LogoID=4&Text={text}&FontSize=70&Color1_color=%23ff0000&Integer1=15&Boolean1=on&Integer9=0&Integer13=on&Integer12=on&BackgroundColor_color=%23ffffff",
            "Flaming": f"LogoID=1169711118&Text={text}&FontSize=90&Color1_color=%234D0000&Integer1=90&Integer9=0&Integer13=on&Integer12=on&BackgroundColor_color=%23FFFFFF",
            "Glitter": f"LogoID=44&Text={text}&FontSize=50&Color1_color=%23FF00AB&Integer1=100&Color2_color=%23FFFFFF&Integer9=0&Integer13=on&Integer12=on&BackgroundColor_color=%23FFB6E7",
            "Love": f"LogoID=4768360740&Text={text}&FontSize=70&Color1_color=%23FF1491&Color2_color=%23FFFFFF&Color3_color=%23FF1491&Integer9=0&Integer13=on&Integer12=on&BackgroundColor_color=%23FFFFFF",
            "Molten Core": f"LogoID=43&Text={text}&FontSize=70&Integer9=0&Integer13=on&Integer12=on&BackgroundColor_color=%23FFFFFF"
        }

        req = requests.post(f"https://cooltext.com/PostChange?{endpoints[text_type.name]}").json()
        await ctx.send(req['renderLocation'].replace('https', 'http'))

    @bot.hybrid_command(name="context", description="Log message context")
    async def context_misc(self, ctx: commands.Context) -> None:
        context = ""
        for var, val in vars(ctx).items():
            context += f"{var}: {val}\n"

        bot_user = await self.bot.fetch_user(self.bot._application.id)
        embed = embedBuilder(bot).embed(
                color=0xffd330,
                author="Context",
                author_avatar=bot_user.avatar,
                description=f"```py\n{context}\n```",
                timestamp=f"{datetime.datetime.now().isoformat()}"
            )
        await ctx.send(embed=embed, ephemeral=True)

    @bot.hybrid_command(name="widepeepohappy", description="Sends a widepeepoHappy emote")
    async def widepeepohappy(self, ctx: commands.Context) -> None:
        await ctx.send('<:WidePeepoHappy1:768481090079686677><:WidePeepoHappy2:768481089936818216><:WidePeepoHappy3:768481090029355038><:WidePeepoHappy4:768481090041413653>')

    @bot.hybrid_command(name="8ball", description="Ask the Magic 8 Ball a question")
    async def magic8ball(self, ctx: commands.Context, question: str) -> None:
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
                    
async def setup(bot):
    await bot.add_cog(Misc(bot))