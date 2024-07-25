import os
import json
import time
from dotenv import find_dotenv, load_dotenv
import discord
from discord.ext import commands
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', owner_id=299556235424956427, intents=intents)

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
OWNER_ID = os.getenv('OWNER_ID')

import misc
from config import config