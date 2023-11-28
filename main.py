import os
from dotenv import find_dotenv, load_dotenv
import discord
from discord import app_commands

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

TOKEN = os.getenv('TOKEN')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!test'):
        await message.channel.send('Hello!')

    twitterLinks = ["https://x.com", "https://twitter.com"]
    for domain in range(len(twitterLinks)):
        if twitterLinks[domain] in message.content:
            fxMessage = message.content.replace(twitterLinks[domain], "https://fxtwitter.com")
            await message.channel.send(fxMessage)

client.run(TOKEN)
