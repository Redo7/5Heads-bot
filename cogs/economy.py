import json
import math
import random
import discord
import sqlite3
from discord import app_commands
from discord.ext import commands, tasks
from discord.app_commands import Choice
from cogs.recruit import execute_query

import os
from dotenv import find_dotenv, load_dotenv
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
TOKEN = os.getenv('TOKEN')
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
        self.currency = "Fetch Name"
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
        print(f"Data ({len(self.user_data)}):{self.user_data}")
        print(f"Economy cog loaded")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        
        await self.earn_currency_by_interacting(message)

    async def earn_currency_by_interacting(self, message):
        balance = self.user_data.get((message.guild.id, message.author.id), 0.0)
        balance += self.epm + (random.random() * 10 / 100)
        self.user_data[(message.guild.id, message.author.id)] = float("%.2f" % balance)
        print(f'Total Balance: {float("%.2f" % balance)}')

    async def add_rand_amount():
        rand_amount = random.random() * 10 # Number 0-10
        rand_amount = math.floor(rand_amount) / 100
        print(rand_amount)
        return rand_amount

    # Task loop stuff
    @tasks.loop(minutes=5.0, reconnect=True)
    async def save_economy(self):
        print("Commiting balance changes to DB")
        query = """
            INSERT OR REPLACE INTO user_balance (server_id, user_id, balance)
            VALUES (?, ?, ?)
        """ # This doesn't work well. It just replicates the entire DB over and over instead of updating the values
        insert_data = [(server_id, user_id, user_balance) for (server_id, user_id), user_balance in self.user_data.items()]
        with database:
            cursor.executemany(query, insert_data)

    def cog_unload(self):
        print("Task loop cancelled")
        self.save_economy.cancel()
    
    def cog_load(self):
        self.save_economy.start()

    @save_economy.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()
    
    # End

async def setup(bot):
    await bot.add_cog(Economy(bot))
