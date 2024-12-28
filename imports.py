import os
import sys
import json
import time
import sqlite3
import asyncio
import requests

from dotenv import find_dotenv, load_dotenv
import discord
from discord import app_commands
from discord.ext import commands

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
OWNER_ID = os.getenv('OWNER_ID')
CLIENT_KEY = os.getenv('CLIENT_KEY')
TENOR_API_KEY = os.getenv('TENOR_API_KEY')
RECRUIT_CHANNEL = int(os.getenv('RECRUIT_CHANNEL'))

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', owner_id=OWNER_ID, intents=intents)

sys.stdout.reconfigure(encoding='utf-8')

from misc import misc
from misc import tenor
from recruit import recruit
from config import config
from admin import admin