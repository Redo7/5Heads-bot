import os
# import time
from dotenv import find_dotenv, load_dotenv
import discord
from discord.ext import commands

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

TOKEN = os.getenv('TOKEN')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))


@bot.command(name="test", description="shrigma ball")
async def test(ctx):
    await ctx.respond("123")


@commands.command(name="sync", hidden=True)
async def sync_commands(self, ctx: commands.Context) -> None:
    resp = await self.bot.tree.sync()
    await ctx.send(f"Syncing slash commands. {len(resp)}")


@bot.event
async def on_message(message):
    # animation_3c = [':OC====3', ':C====3', '¦C===3', ':C==3', ':C=3', ':C3',
    #                 '¦3', ':3', '¦3', ':C3', ':C=3', '¦C3', ':C=3', ':C3', ':3']
    # if ":3C====3" in message.content and message.author == bot.user:
    #     for frame in animation_3c:
    #         await message.edit(content=frame)
    #         time.sleep(0.4)

    if message.author == bot.user:
        return

    # if ":3" in message.content:
    #    await message.channel.send(":3C====3")

    # twitter_links = ["https://x.com", "https://twitter.com"]
    # for link in twitter_links:
    #     if message.content.startswith(link) and "/status/" in message.content:
    #         await message.channel.send(message.content.replace(link, "https://fxtwitter.com"))

bot.run(TOKEN)
