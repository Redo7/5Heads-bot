import os
import sys
import time
import asyncio
import discord
import traceback
import datetime
from discord import app_commands
from discord.ext import commands, tasks
from cogs.discordIntegration import *
from cogs.embedBuilder import embedBuilder
from prometheus_client import start_http_server, Counter, Gauge, Histogram, Enum
start_time = time.perf_counter()


from dotenv import find_dotenv, load_dotenv
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
TOKEN = os.getenv('TOKEN')
OWNER_ID = int(os.getenv('OWNER_ID'))
RECRUIT_CHANNEL = int(os.getenv('RECRUIT_CHANNEL'))
intents = discord.Intents.default()
intents.message_content = True

COMMAND_COUNTER = Counter('commands_total', 'Total commands executed', ['command_name'])
COMMAND_DURATION = Histogram('command_duration', 'Command execution time', ['command_name'])
STARTUP_DURATION = Histogram('startup_duration', 'Bot startup time')
UPTIME = Gauge('bot_uptime', 'Bot uptime (timestamp)')

class Custom_help(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        e = embedBuilder(bot).embed(
                color = "#ffd330",
                description = ''
                )
        for page in self.paginator.pages:
            e.description += page
        await destination.send(embed=e)

    def add_command_formatting(self, command):
        if command.description:
            self.paginator.add_line(f"**{command.name}** - {command.description}")
        else:
            self.paginator.add_line(f"**{command.name}** - No description available")

        usage_line = f"Usage: `{self.context.clean_prefix}{command.name}"
        if hasattr(command, "app_command") and command.app_command is not None:
            for param in command.app_command.parameters:
                if param.required:
                    usage_line += f" <{param.name}>"
                else:
                    usage_line += f" [{param.name}]"
        usage_line += "`"
        self.paginator.add_line(usage_line)

        if hasattr(command, "app_command") and command.app_command is not None:
            self.paginator.add_line("\n**Arguments:**")
            for param in command.app_command.parameters:
                description = param.description or "No description available"
                if hasattr(param, "choices") and param.choices:
                    choices = ", ".join([f"`{choice.name}`" for choice in param.choices])
                    description += f"\nChoices: {choices}"
                self.paginator.add_line(f"- `{param.name}`: {description}")

bot = commands.Bot(command_prefix='!', owner_id=OWNER_ID, intents=intents)
bot.help_command = Custom_help()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

    for command in bot.commands:
        COMMAND_COUNTER.labels(command_name=command.name).inc(0)
        COMMAND_DURATION.labels(command_name=command.name).observe(0)

    if not update_uptime.is_running():
        update_uptime.start()

    STARTUP_DURATION.observe((time.perf_counter() - start_time))
    
    if os.getenv('TOKEN') == os.getenv('DEV'): return
    embed = embedBuilder(bot).embed(
            color="#75FF81",
            author=bot.user,
            author_avatar=bot.user.avatar,
            description=f"**Bot is online**",
            timestamp=f"{datetime.datetime.now().timestamp()}"
        )
    await discordIntegration(bot).send_embed(OWNER_ID, embed)


async def load():
    await bot.load_extension(f"cogs.economy") # Load economy first to prevent access errors
    print(f"Loading economy cog")
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and "economy" not in filename:
            print(f"Loading {filename[:-3]} cog")
            await bot.load_extension(f"cogs.{filename[:-3]}")

@bot.event
async def on_command_error(ctx: commands.Context, error):
    traceback_str = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
    if isinstance(error, commands.CommandNotFound):
        title = "Command not found. Please check the command and try again."
    elif isinstance(error, commands.MissingRequiredArgument):
        title = "Missing required argument. Please check the command usage."
    elif isinstance(error, commands.BadArgument):
        title = "Invalid argument. Please check the command usage."
    elif isinstance(error, commands.CommandInvokeError):
        # Send the error and traceback
        title = "An error occurred while executing the command."
        print(traceback_str)
    else:
        title = "An unexpected error occurred."
        print(traceback_str)
    try:
        embed = embedBuilder(bot).embed(
                color="#ed1b53",
                author=title,
                author_avatar=bot.user.avatar,
                description=f"```py\n{error}\n```",
                timestamp=f"{datetime.datetime.now().timestamp()}"
            )
        await ctx.send(embed=embed, ephemeral=True)
    except Exception as e: print(e)

@tasks.loop(seconds=10, reconnect=True)
async def update_uptime():
    UPTIME.set(time.perf_counter() - start_time)

@update_uptime.before_loop
async def before_loop():
    await bot.wait_until_ready()

async def main():
    await load()  # Load the cogs
    start_http_server(5555)
    await bot.start(TOKEN)

asyncio.run(main())
sys.stdout.reconfigure(encoding='utf-8')