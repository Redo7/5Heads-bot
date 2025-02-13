import json
import math
import random
import discord
import sqlite3
import datetime
from typing import Optional
from discord.ext import commands, tasks
from discord import ui
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

    # on message

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

    @commands.hybrid_command(name='sendfunds', brief='Transfer funds to a member')
    async def send_funds(self, ctx, target: discord.User, amount: int):
        sender = await self.bot.fetch_user(ctx.author.id)
        sender_balance = await self.get_user_balance(ctx.guild.id, sender.id)
        target = await self.bot.fetch_user(target.id)

        if(sender_balance < amount):
            await ctx.send("You too broke for that")
            return
        if amount <= 0:
            await ctx.send("Nah uh")
            return
        
        await self.subtract_money(amount, ctx.guild.id, sender.id)
        await self.add_money(amount, ctx.guild.id, target.id)
        embed = embedBuilder(bot).embed(
            color=0xffd330,
            author=sender.display_name,
            author_avatar=sender.display_avatar,
            title=f"Sent {amount} {self.currency} to {target.display_name}",
            thumbnail=target.display_avatar,
            timestamp=f"{datetime.datetime.now().isoformat()}",
            )
        await ctx.send(f"{target.mention}", embed=embed)

    @commands.hybrid_command(name='requestfunds', brief='Request funds from a member')
    async def request_funds(self, ctx, target: discord.User, amount: int):
        if amount <= 0:
            await ctx.send("Nah uh")
            return
        sender = await self.bot.fetch_user(ctx.author.id)
        target = await self.bot.fetch_user(target.id) # This is the person transfering the funds / the target of the command
        embed = embedBuilder(bot).embed(
            color=0xffd330,
            author=target.display_name,
            author_avatar=target.display_avatar,
            title=f"{sender.display_name} requests a transfer of {amount} {self.currency}",
            thumbnail=sender.display_avatar,
            timestamp=f"{datetime.datetime.now().isoformat()}",
            )
        await ctx.send(f"{target.mention}", embed=embed, view=self.transferView(bot, ctx.guild.id, sender, target, amount, self))

    class transferView(ui.View):
        def __init__(self, bot, guild_id, sender, target, amount, economy, timeout=180):
            super().__init__(timeout=timeout)
            self.bot = bot
            self.guild_id = guild_id
            self.sender = sender
            self.target = target
            self.amount = amount
            self.economy = economy

        @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
        async def accept(self, interaction: discord.Interaction, button: ui.Button):
            if interaction.user.id != self.target.id: return
            await interaction.message.delete()
            if self.amount > await self.economy.get_user_balance(self.guild_id, self.target.id):
                embed = embedBuilder(bot).embed(
                    color=0xed1b53,
                    author=self.sender.display_name,
                    author_avatar=self.sender.display_avatar,
                    description=f"Insufficient funds. Transaction did not occur.",
                    timestamp=f"{datetime.datetime.now().isoformat()}",
                    )
                await interaction.response.send_message(embed=embed)
                return
            await self.economy.subtract_money(self.amount, self.guild_id, self.target.id)
            await self.economy.add_money(self.amount, self.guild_id, self.sender.id)
            embed = embedBuilder(bot).embed(
                color=0x75FF81,
                author=self.target.display_name,
                author_avatar=self.target.display_avatar,
                title=f"Sent {self.amount} {self.economy.currency} to {self.sender.display_name}",
                thumbnail=self.sender.display_avatar,
                timestamp=f"{datetime.datetime.now().isoformat()}",
                )
            await interaction.response.send_message(f"{self.sender.mention}", embed=embed)
        
        @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
        async def decline(self, interaction: discord.Interaction, button: ui.Button):
            if interaction.user.id != self.target.id: return
            await interaction.message.delete()
            embed = embedBuilder(bot).embed(
                color=0xed1b53,
                author=self.target.display_name,
                author_avatar=self.target.display_avatar,
                description=f"Transaction declined.",
                timestamp=f"{datetime.datetime.now().isoformat()}",
                )
            await interaction.response.send_message(f"{self.sender.mention}", embed=embed)
    
    # End

async def setup(bot):
    await bot.add_cog(Economy(bot))
