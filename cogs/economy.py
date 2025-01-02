import json
import discord
import sqlite3
from discord import app_commands
from discord.ext import commands
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
database.execute('CREATE TABLE IF NOT EXISTS user_balance(server_id INT, user_id INT, balance INT)')

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.currency = "Fetch Name"
        data = cursor.execute("SELECT * FROM user_balance").fetchall()
        self.user_data = {}
        for entry in data:
            server_id = entry[0]
            user_id = entry[1]
            user_balance = entry[2]
            self.user_data[(server_id, user_id)] = user_balance
        print(self.user_data)
        # balance = self.user_data.get((server_id, user_id), 0)  # Default balance to 0 if not found

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Economy cog loaded")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

    async def earn_currency_by_interacting(self, user_id):
        data = cursor.execute('SELECT balance FROM user_balance WHERE user_id = ?', (user_id,)).fetchone()
        print(data)

async def setup(bot):
    await bot.add_cog(Economy(bot))
