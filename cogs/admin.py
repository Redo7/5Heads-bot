import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice

import os
from dotenv import find_dotenv, load_dotenv
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
intents = discord.Intents.default()
intents.message_content = True
OWNER_ID = int(os.getenv('OWNER_ID'))
bot = commands.Bot(command_prefix='!', owner_id=OWNER_ID, intents=intents)

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.owner_id = int(os.getenv('OWNER_ID'))

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Admin cog loaded")

    @bot.hybrid_command(name="sync", description="Syncs commands", hidden=True)
    async def sync(self, ctx):
        if ctx.author.id != OWNER_ID:
            await ctx.send("Nah uh")
            return
        resp = await self.bot.tree.sync()   
        msg = f"Syncing {len(resp)} commands."  
        await ctx.send(msg) 
        print(msg)  

    @commands.has_permissions(manage_messages=True)
    @bot.hybrid_command(name='purge', brief='Deletes a specified number of messages from the current channel')
    async def purge(self, ctx, amount: int):
        await ctx.send(f'Purging messages...')
        deleted = await ctx.channel.purge(limit=amount)
        if len(deleted) == 0:
            embed = discord.Embed(title='Purge "complete"', color=0xED1B53)
            embed.description = 'No messages were deleted (bruh)'
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title='Purge complete', color=0x75FF81)
            embed.description = f'{len(deleted)} messages were deleted'
            await ctx.send(embed=embed)
    
    # @commands.hybrid_command(name='help', brief='Displays the help documentation') # Todo
    # async def help(self, ctx, command_name):
    #         command = self.bot.get_command(command_name)
    #         print(command, command.help)
    #         if command:
    #             await ctx.send(command.help)
    #         else:
    #             await ctx.send(f"Command '{command_name}' not found.")

async def setup(bot):
    await bot.add_cog(Admin(bot))