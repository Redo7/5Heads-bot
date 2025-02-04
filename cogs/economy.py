import json
import math
import random
import discord
import sqlite3
import datetime
from typing import Optional
from discord import app_commands
from discord.ext import commands, tasks
from discord.app_commands import Choice
from cogs.recruit import execute_query
from cogs.embedBuilder import embedBuilder

import os
from dotenv import find_dotenv, load_dotenv
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
intents = discord.Intents.default()
intents.message_content = True
OWNER_ID = int(os.getenv('OWNER_ID'))
bot = commands.Bot(command_prefix='!', owner_id=OWNER_ID, intents=intents)

database = sqlite3.connect('db/main.db')
cursor = database.cursor()
database.execute('CREATE TABLE IF NOT EXISTS economy(server_id INT, currency TEXT, epm REAL)')
database.execute('CREATE TABLE IF NOT EXISTS user_balance(server_id INT, user_id INT, balance FLOAT, PRIMARY KEY (server_id, user_id))')

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.currency = "5Head Coins"
        self.epm = 0.5
        data = cursor.execute("SELECT * FROM user_balance").fetchall()
        self.user_data = {}
        for entry in data:
            server_id = entry[0]
            user_id = entry[1]
            user_balance = entry[2]
            self.user_data[(server_id, user_id)] = user_balance

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Economy cog loaded")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        
        await self.add_money(self.epm + (random.random() * 10 / 100), message.guild.id, message.author.id)

    # Methods

    async def add_money(self, add_balance, guild_id, user_id):
        balance = await self.get_user_balance(guild_id, user_id)
        balance += add_balance
        self.user_data[(guild_id, user_id)] = float("%.2f" % balance)
    
    async def subtract_money(self, sub_balance, guild_id, user_id):
        balance = await self.get_user_balance(guild_id, user_id)
        balance -= sub_balance
        self.user_data[(guild_id, user_id)] = float("%.2f" % balance)

    async def get_user_balance(self, guild_id, user_id):
        user_balance = self.user_data.get((guild_id, user_id), 0.0)
        return user_balance

    # Task Loop

    @tasks.loop(minutes=5.0, reconnect=True)
    async def save_economy(self):
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Commiting balance changes to DB (economy)")
        query = """
            INSERT OR REPLACE INTO user_balance (server_id, user_id, balance)
            VALUES (?, ?, ?)
        """
        insert_data = [(server_id, user_id, user_balance) for (server_id, user_id), user_balance in self.user_data.items()]
        with database:
            cursor.executemany(query, insert_data)
            database.commit()

    def cog_load(self):
        print("Economy task loop started")
        self.save_economy.start()

    def cog_unload(self):
        print("Economy task loop cancelled")
        self.save_economy.cancel()

    @save_economy.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()
    
    # Commands

    @commands.hybrid_command(name='balance', brief='Check your balance')
    async def balance(self, ctx, show_off: Optional[bool]):
        await self.save_economy()
        if show_off == None: show_off = False
        user = await self.bot.fetch_user(ctx.author.id)
        balance = await self.get_user_balance(ctx.guild.id, ctx.author.id)
        embed = embedBuilder(bot).embed(
            color=0xffd330,
            author=user.display_name,
            author_avatar=user.avatar,
            description=f"Your current balance is ***{balance}*** {self.currency}",
            )
        await ctx.send(embed=embed, ephemeral=not show_off)

    # End

async def setup(bot):
    await bot.add_cog(Economy(bot))
