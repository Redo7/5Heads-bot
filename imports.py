import os
import json
import time
import sqlite3
from dotenv import find_dotenv, load_dotenv
import discord
from discord import app_commands
from discord.ext import commands

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
OWNER_ID = os.getenv('OWNER_ID')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', owner_id=OWNER_ID, intents=intents)

import misc
from config import config