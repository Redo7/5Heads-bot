import json
import math
import random
import discord
import sqlite3
import datetime
from typing import Optional
from discord.ext import commands, tasks
from discord import ui, app_commands
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
        data = cursor.execute("SELECT * FROM economy").fetchall()
        self.server_data = {}
        for entry in data:
            self.server_data[entry[0]] = {"currency": entry[1], "epm": entry[2]}
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
    async def on_guild_join(self, guild):
        query = 'SELECT * FROM economy WHERE server_id = ?'
        data = cursor.execute(query, (guild.id,)).fetchall()   
        if data != [] and guild.id == data[0][0]:
            print(f'[Economy] Joined "{guild}" ({guild.id}), but found an existing database entry. Skipping...')
            return
        else:
            print(f'[Economy] Creating new database entry for "{guild}" ({guild.id})')
            query = 'INSERT INTO economy (server_id, currency, epm) VALUES (?, ? ,?)'
            cursor.execute(query, (guild.id, self.currency, self.epm))
            database.commit()

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
        
        await self.add_money(self.server_data[message.guild.id]["epm"] + (random.random() * 10 / 100), message.guild.id, message.author.id)

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

    @commands.hybrid_command(name='balance', description='Check your balance')
    @app_commands.describe(show_off="Should the message be sent publicly?")
    async def balance(self, ctx, show_off: Optional[bool]):
        await self.save_economy()
        if show_off == None: show_off = False
        user = await self.bot.fetch_user(ctx.author.id)
        balance = await self.get_user_balance(ctx.guild.id, ctx.author.id)
        embed = embedBuilder(bot).embed(
            color="#ffd330",
            author=user.display_name,
            author_avatar=user.avatar,
            description=f"Your current balance is ***{balance}*** {self.server_data[ctx.guild.id]['currency']}",
            )
        await ctx.send(embed=embed, ephemeral=not show_off)

    @commands.has_permissions(administrator=True)
    @bot.hybrid_command(name='epm', description='Changes the "Earnings Per Message" value for the current server')
    @app_commands.describe(amount="The amount users earn per message sent")
    async def epm(self, ctx, amount: float):
        prev_amount = self.server_data[ctx.guild.id]["epm"]
        self.server_data[ctx.guild.id]["epm"] = amount
        cursor.execute(f"UPDATE economy SET epm = (?) WHERE server_id = (?)", (amount, ctx.guild.id,))
        database.commit()
        embed = embedBuilder(bot).embed(
            color="#ffd330",
            author_avatar=self.bot.user.avatar,
            author="5Head",
            description=f"EPM for **`{ctx.guild.name}`** was adjusted to **`{amount}`**",
            footer=f"Previous amount: {prev_amount}"
            )
        await ctx.send(embed=embed, ephemeral=True)

    @commands.has_permissions(administrator=True)
    @bot.hybrid_command(name='currency', description='Changes the currency name for the current server')
    @app_commands.describe(name="The new currency name")
    async def currency(self, ctx, name: str):
        prev_name = self.server_data[ctx.guild.id]["currency"]
        self.server_data[ctx.guild.id]["currency"] = name
        cursor.execute(f"UPDATE economy SET currency = (?) WHERE server_id = (?)", (name, ctx.guild.id,))
        database.commit()
        embed = embedBuilder(bot).embed(
            color="#ffd330",
            author_avatar=self.bot.user.avatar,
            author="5Head",
            description=f"**`{name}`** is now the currency in **`{ctx.guild.name}`**",
            footer=f"Previous name: {prev_name}"
            )
        await ctx.send(embed=embed, ephemeral=True)

    @commands.hybrid_command(name='sendfunds', description='Transfer funds to a member')
    @app_commands.describe(target="The user to send the funds to")
    @app_commands.describe(amount="The amount of funds to sends")
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
            color="#ffd330",
            author=sender.display_name,
            author_avatar=sender.display_avatar,
            title=f"Sent {amount} {self.server_data[ctx.guild.id]['currency']} to {target.display_name}",
            thumbnail=target.display_avatar,
            timestamp=f"{datetime.datetime.now().timestamp()}",
            )
        await ctx.send(f"{target.mention}", embed=embed)

    @commands.hybrid_command(name='requestfunds', description='Request funds from a member')
    @app_commands.describe(target="The user to request the funds from")
    @app_commands.describe(amount="The amount of funds to request")
    async def request_funds(self, ctx, target: discord.User, amount: int):
        if amount <= 0:
            await ctx.send("Nah uh")
            return
        sender = await self.bot.fetch_user(ctx.author.id)
        target = await self.bot.fetch_user(target.id) # This is the person transfering the funds / the target of the command
        embed = embedBuilder(bot).embed(
            color="#ffd330",
            author=target.display_name,
            author_avatar=target.display_avatar,
            title=f"{sender.display_name} requests a transfer of {amount} {self.server_data[ctx.guild.id]['currency']}",
            thumbnail=sender.display_avatar,
            timestamp=f"{datetime.datetime.now().timestamp()}",
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
                    color="#ed1b53",
                    author=self.sender.display_name,
                    author_avatar=self.sender.display_avatar,
                    description=f"Insufficient funds. Transaction did not occur.",
                    timestamp=f"{datetime.datetime.now().timestamp()}",
                    )
                await interaction.response.send_message(embed=embed)
                return
            await self.economy.subtract_money(self.amount, self.guild_id, self.target.id)
            await self.economy.add_money(self.amount, self.guild_id, self.sender.id)
            embed = embedBuilder(bot).embed(
                color="#75FF81",
                author=self.target.display_name,
                author_avatar=self.target.display_avatar,
                title=f"Sent {self.amount} {self.economy.currency} to {self.sender.display_name}",
                thumbnail=self.sender.display_avatar,
                timestamp=f"{datetime.datetime.now().timestamp()}",
                )
            await interaction.response.send_message(f"{self.sender.mention}", embed=embed)
        
        @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
        async def decline(self, interaction: discord.Interaction, button: ui.Button):
            if interaction.user.id != self.target.id: return
            await interaction.message.delete()
            embed = embedBuilder(bot).embed(
                color="#ed1b53",
                author=self.target.display_name,
                author_avatar=self.target.display_avatar,
                description=f"Transaction declined.",
                timestamp=f"{datetime.datetime.now().timestamp()}",
                )
            await interaction.response.send_message(f"{self.sender.mention}", embed=embed)
    
    # End

async def setup(bot):
    await bot.add_cog(Economy(bot))
