import time
import os
import time
import asyncio
from cogs import config

import discord
from discord.ext import commands
OWNER_ID = os.getenv('OWNER_ID')
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', owner_id=OWNER_ID, intents=intents)

class onMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.twitter_links = ["https://x.com", "https://twitter.com"]
        self.animation_3c = [':OC====3', ':C====3', '¦C===3', ':C==3', ':C=3', ':C3',
                        '¦3', ':3', '¦3', ':C3', ':C=3', '¦C3', ':C=3', ':C3', ':3']


    @commands.Cog.listener()
    async def on_ready(self):
        print(f"On_message cog loaded")

    @commands.Cog.listener()
    async def on_message(self, message):
        if ":3C====3" in message.content and message.author == self.bot.user:
            for frame in self.animation_3c:
                await message.edit(content=frame)
                time.sleep(0.4)

        if message.author == self.bot.user:
            return

        if ":3" in message.content and config.check_db(message.guild.id, 'animation_3c') == 1:
            await message.channel.send(":3C====3")

        for link in self.twitter_links:
            if link in message.content and "/status/" in message.content and config.check_db(message.guild.id, 'twitter_links') == 1:
                msg_split = message.content.split(' ')
                indices = [i for i, s in enumerate(msg_split) if link in s]
                new_msg = await message.channel.send(msg_split[indices[0]].replace(link, "https://fxtwitter.com"))
                
                await new_msg.add_reaction('✔️')
                await new_msg.add_reaction('✖️')

                def check(reaction, user):
                    return user == message.author
                
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=10.0, check=check)
                except asyncio.TimeoutError:
                    await new_msg.delete()
                else:
                    if reaction.emoji == '✖️':
                        await new_msg.delete()
                    elif reaction.emoji == '✔️':
                        await new_msg.clear_reactions()

async def setup(bot):
    await bot.add_cog(onMessage(bot))