import time
import random
import asyncio
from cogs import config

import discord
from discord import app_commands
from discord.ext import commands

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

    @bot.hybrid_command(name="context", description="Log message context")
    async def context_misc(self, ctx: commands.Context) -> None:
        context = ""
        for var, val in vars(ctx).items():
            context += f"{var}: {val}\n"
        print(context)
        await ctx.send("Done")

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