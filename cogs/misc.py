import re
import math
import json
import uuid
import random
import sqlite3
import datetime
import requests
from cogs import config
from typing import Optional
from cogs.embedBuilder import embedBuilder

import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button
from discord.app_commands import Choice

import os
OWNER_ID = os.getenv('OWNER_ID')
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', owner_id=OWNER_ID, intents=intents)

database = sqlite3.connect('db/main.db')
cursor = database.cursor()
database.execute('CREATE TABLE IF NOT EXISTS blacklist(server_id INT, listing_id INT DEFAULT 0, name TEXT, link TEXT, reason TEXT, added_by INT, timestamp INT)')

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Misc cog loaded")

    @bot.hybrid_command(name="blacklistadd", description="Add a new entry to the wall of shame")
    async def blacklist_add(self, ctx, name: str, link: str, reason: str):
        if ctx.interaction is None: 
            raise ValueError('This command can only be used as /blacklistadd')
        if re.compile(r".+([A-Za-z]+(\.[A-Za-z]+)+).+", re.IGNORECASE).match(link) is None:
            raise ValueError('The value in the link field does not resemble a link.\nExpected: https://site.com/username OR site.com/username')
        if "http://" not in link or "https://" not in link:
            link = f"https://{link}"
        # Search for existing listing
        existing_listing = await self.check_listing_exist(name, link)
        largest_id = await self.get_largest_id()
        # Replace content to match the previous listing
        listing_id = 0
        if existing_listing:
            listing_id = existing_listing[1]
            name = existing_listing[2]
            link = existing_listing[3]
        else:
            if not largest_id:
                largest_id = 1
            else:
                listing_id = max(max(tup) for tup in largest_id) + 1

        timestamp = math.floor(datetime.datetime.now().timestamp())
        author = await self.bot.fetch_user(ctx.author.id)

        query = "INSERT INTO blacklist (server_id, listing_id, name, link, reason, added_by, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)"
        cursor.execute(query, (ctx.guild.id, listing_id, name, link, reason, ctx.author.id, timestamp))
        database.commit()

        server = await self.bot.fetch_guild(ctx.guild.id)
        embed = embedBuilder(bot).embed(
                color=0xffd330,
                author=f"{server.name} blacklist",
                author_avatar=server.icon,
                title="New entry",
                description=f"**[{name}]({link})**\n{reason}\n-# Added <t:{timestamp}:R> by {author.display_name}",
                footer=f"ID: {listing_id}"
            )
        await ctx.send(embed=embed)
    
    async def check_listing_exist(self, name, link):
        data = cursor.execute("SELECT * from blacklist WHERE name = ? OR link = ?", (name, link)).fetchone()
        database.commit()
        return data

    async def get_largest_id(self):
        data = cursor.execute("SELECT listing_id from blacklist").fetchall()
        database.commit()
        return data

    @bot.hybrid_command(name="blacklist", description="Show the wall of shame or a specific entry")
    async def blacklist(self, ctx, listing_id: Optional[int]):
        description = ""
        server = await self.bot.fetch_guild(ctx.guild.id)
        if listing_id is None:
            entries = cursor.execute("SELECT * from blacklist WHERE server_id = ?", (ctx.guild.id,)).fetchall()
            unique_dict = {}
            for entry in entries:
                key = entry[1]
                if key not in unique_dict:
                    unique_dict[key] = entry
            unique_data = list(unique_dict.values())
            for entry in unique_data:
                description += f"**[{entry[1]}]** [{entry[2]}]({entry[3]})\n"
            embed = embedBuilder(bot).embed(
                color=0xffd330,
                author=f"{server.name} blacklist",
                author_avatar=server.icon,
                description=description,
                footer="Use /blacklist {id} for more information about the entry."
            )
        else:
            entries = cursor.execute("SELECT * from blacklist WHERE listing_id = ?", (listing_id,)).fetchall()
            if len(entries) is 0: raise ValueError("No entry with a given ID exists.")
            for entry in entries:
                reason = entry[4]
                author = await self.bot.fetch_user(entry[5])
                timestamp = entry[6]
                description += f"-# Added <t:{timestamp}:R> by {author.display_name}:\n{reason}\n\n"
            embed = embedBuilder(bot).embed(
                color=0xffd330,
                author=f"{server.name} blacklist",
                author_avatar=server.icon,
                description=f"### [{entries[0][2]}]({entries[0][3]})\n{description}"
            )
        await ctx.send(embed=embed)

    @bot.hybrid_command(name="blacklistdelete", description="Delete an entry from the wall of shame")
    @app_commands.checks.has_permissions(administrator=True)
    async def blacklist_delete(self, ctx, listing_id: int):
        entry = cursor.execute("SELECT * FROM blacklist WHERE listing_id = ?", (listing_id,)).fetchone()
        if entry is None: raise ValueError("No entry with a given ID exists.")
        timestamp = math.floor(datetime.datetime.now().timestamp()) + 60
        server = await self.bot.fetch_guild(ctx.guild.id)
        embed = embedBuilder(bot).embed(
                color=0xffd330,
                author=f"{server.name} blacklist",
                author_avatar=server.icon,
                description=f"### This will delete the entry for: [{entry[2]}]({entry[3]})\nAre you sure?\nThis window will timeout <t:{timestamp}:R>"
            )
        await ctx.send(embed=embed, view=self.Blacklist(bot, ctx, entry))

    class Blacklist(View):
        def __init__(self,bot, ctx, entry, timeout=60):
            super().__init__(timeout=timeout)
            self.bot = bot
            self.ctx = ctx
            self.entry = entry
        
        @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
        async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user.id != self.ctx.author.id: return
            cursor.execute("DELETE FROM blacklist WHERE listing_id = ?", (self.entry[1],))
            database.commit()
            server = await self.bot.fetch_guild(self.ctx.guild.id)
            embed = embedBuilder(bot).embed(
                color=0x75FF81,
                author=f"{server.name} Blacklist",
                author_avatar=server.icon,
                description=f"### Entry for [{self.entry[2]}]({self.entry[3]}) was deleted."
            )
            await interaction.response.send_message(embed=embed, view=None)


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