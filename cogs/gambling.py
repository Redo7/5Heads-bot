import random
import discord
import sqlite3
import datetime
from typing import Optional
from discord.ext import commands, tasks
from cogs.embedBuilder import embedBuilder
from discord import ui, app_commands

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
database.execute('CREATE TABLE IF NOT EXISTS gambling(server_id INT PRIMARY KEY, jackpot REAL DEFAULT 500.0)')

class Gambling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.economy = bot.get_cog("Economy")
        self.gambling_data = {
            "jackpot": {},
            "roulette": {
                "green": [0],
                "black": [2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35],
                "red": [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]
            }
        }
        data = cursor.execute("SELECT * FROM gambling").fetchall()
        for entry in data:
            server_id = entry[0]
            amount = entry[1]
            self.gambling_data["jackpot"][server_id] = amount
        self.emotes = {
            "slot1": ["<a:despairge1:1336359123016749067>", "<a:kys1:1336359185725784164>", "<a:widepeepohappy1:1336359213579894795>", "<a:7271:1336359092125696000>", "<a:jackpot1:1336359154012389428>"],
            "slot2": ["<a:despairge2:1336359131216478299>", "<a:kys2:1336359195225886782>", "<a:widepeepohappy2:1336359223264808991>", "<a:7272:1336359103156588584>", "<a:jackpot2:1336359167522373653>"],
            "slot3": ["<a:despairge3:1336359144214630452>", "<a:kys3:1336359203299790878>", "<a:widepeepohappy3:1336359231636635662>", "<a:7273:1336359112660877403>", "<a:jackpot3:1336359177395634219>"]
        }

        if os.getenv('TOKEN') == os.getenv('DEV'):
            self.emotes = {
            "slot1": ["<a:despairge1:1336349534552330270>", "<a:kys1:1336349591636934831>", "<a:widepeepohappy1:1336349619256295506>", "<a:7271:1336349465690247208>", "<a:jackpot1:1336349564403322912>"],
            "slot2": ["<a:despairge2:1336349544790622330>", "<a:kys2:1336349602265432074>", "<a:widepeepohappy2:1336349628492419102>", "<a:7272:1336349515774431334>", "<a:jackpot2:1336349573953749023>"],
            "slot3": ["<a:despairge3:1336349553061793944>", "<a:kys3:1336349611639570506>", "<a:widepeepohappy3:1336349636255944746>", "<a:7273:1336349524985122957>", "<a:jackpot3:1336349581679530007>"]
        }
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Gambling cog loaded")

    @bot.event
    async def on_guild_join(self, guild):
        query = 'SELECT * FROM gambling WHERE server_id = ?'
        data = cursor.execute(query, (guild.id,)).fetchall()   
        if data != [] and guild.id == data[0][0]:
            print(f'[Gambling] Joined "{guild}" ({guild.id}), but found an existing database entry. Skipping...')
            return
        else:
            print(f'[Gambling] Creating new database entry for "{guild}" ({guild.id})')
            query = 'INSERT INTO gambling (server_id) VALUES (?)'
            cursor.execute(query, (guild.id,))
            database.commit()

    # Task Loop

    @tasks.loop(minutes=5.0, reconnect=True)
    async def save_gambling(self):
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Commiting balance changes to DB (gambling)")
        query = """
            INSERT OR REPLACE INTO gambling (server_id, jackpot)
            VALUES (?, ?)
            ON CONFLICT(server_id) DO UPDATE SET jackpot = excluded.jackpot;
        """
        insert_data = [(server_id, jackpot) for server_id, jackpot in self.gambling_data["jackpot"].items()]

        with database:
            cursor.executemany(query, insert_data)
            database.commit()

    def cog_load(self):
        print("Gambling task loop started")
        self.save_gambling.start()

    def cog_unload(self):
        print("Gambling task loop cancelled")
        self.save_gambling.cancel()

    @save_gambling.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()

    async def check_bet_balance(self, ctx, bet):
        user_balance = await self.economy.get_user_balance(ctx.guild.id, ctx.author.id)
        if user_balance < bet:
            await ctx.send("broke ahh", ephemeral=True)
            return True
        elif bet <= 0:
            await ctx.send("nah uh", ephemeral=True)
            return True

    # Slots

    @bot.tree.command(name='slots', description='Spin to win!')
    async def slots(self, interaction: discord.Interaction, spins: Optional[int]):
        spins = 1 if spins == None else spins
        if spins > 4:
            await interaction.response.send_message("You can only do up to 4 spins at a time", ephemeral=True)
            return
        win_con = {
            f'{self.emotes["slot1"][0]}': 25,
            f'{self.emotes["slot1"][1]}': 75,
            f'{self.emotes["slot1"][2]}': 150,
            f'{self.emotes["slot1"][3]}': 300,
            f'{self.emotes["slot1"][4]}': 500
        }
        required_amount = 10
        user_balance = await self.economy.get_user_balance(interaction.guild_id, interaction.user.id)
        jackpot = await self.get_jackpot(interaction.guild_id, "get", 0)
        if user_balance < required_amount * spins:
            await interaction.response.send_message("broke ahh", ephemeral=True)
            return

        description = ""
        slots_split = []
        for spin in range(1, spins + 1):
            slots = ""
            for emote in range(1, 4):
                slots += f'{random.choice(self.emotes[f"slot{emote}"])} '
            
            slots_split += [slots.split(' ')]
            slots = slots.replace(' ', '')
            if self.emotes["slot1"].index(slots_split[spin - 1][0]) == self.emotes["slot2"].index(slots_split[spin - 1][1]) == self.emotes["slot3"].index(slots_split[spin - 1][2]):
                spin = f"{spin} ✅"
            if os.getenv('TOKEN') == os.getenv('DEV'):
                description += f"""
                    # `Spin #{spin}`\n
                    # <:R1_1:1333784956459155509><:R1_2:1333784966902845521><:R1_3:1333784977254514738><:R1_4:1333784986133991516><:R1_5:1333784994774253589>\n
                    # <:R2_1:1333780034954989639>{slots}<:R2_5:1333780071382650910>\n
                    # <:R3_1:1333780086113177600><:R3_2:1333780096179372062><:R3_3:1333780106648227881><:R3_4:1333780115959713792><:R3_5:1333780125954609193>\n
                    # <:R4_1:1333780136864251975><:R4_2:1333780143918809100><:R4_3:1333780152202821684><:R4_4:1333780160675319839><:R4_5:1333780168212480010>\n
                    # <:R5_1:1333780176504623114><:R5_2:1333780264564035584><:R5_3:1333780274860789772><:R5_4:1333780283656241256><:R5_5:1333780292246175784>\n
                """
            else:
                description += f"""
                    # `Spin #{spin}`\n
                    # <:R1_1:1336358772888567868><:R1_2:1336358785802829846><:R1_3:1336358794225127505><:R1_4:1336358802928173067><:R1_5:1336358810918584380>\n
                    # <:R2_1:1336358821530042470>{slots}<:R2_5:1336358832745480233>\n
                    # <:R3_1:1336358841344069725><:R3_2:1336358854044156086><:R3_3:1336358867164205056><:R3_4:1336358885635653786><:R3_5:1336358900471037973>\n
                    # <:R4_1:1336358909299916830><:R4_2:1336358917780930603><:R4_3:1336358929126522932><:R4_4:1336358940635693157><:R4_5:1336358950127538336>\n
                    # <:R5_1:1336359019560042658><:R5_2:1336359027994791997><:R5_3:1336359038895652907><:R5_4:1336359049972678757><:R5_5:1336359059300941935>\n
                """

        embed = embedBuilder(bot).embed(
            color=0xffd330,
            author="Slots",
            description=description,
            footer=f"Jackpot stash: {jackpot}"
            )

        eph = True
        spins_won = 0
        winnings = 0

        for spin in range(len(slots_split)):
            if self.emotes["slot1"].index(slots_split[spin][0]) == self.emotes["slot2"].index(slots_split[spin][1]) == self.emotes["slot3"].index(slots_split[spin][2]):
                spins_won += 1
                if eph:
                    eph = False
                winnings += win_con[f'{slots_split[spin][0]}']
                if slots_split[spin][0] == self.emotes["slot1"][4]:
                    winnings += await self.get_jackpot(interaction.guild_id, "subtract", 0)
                await self.economy.add_money(winnings, interaction.guild_id, interaction.user.id)
                followup = f"Winning spins: **{spins_won}**\nYou won: **{winnings}** {self.economy.currency}!"
            else:
                await self.economy.subtract_money(required_amount, interaction.guild_id, interaction.user.id)
                await self.get_jackpot(interaction.guild_id, "add", required_amount * 0.25)
                if spins_won == 0:
                    followup = "You won fuck all!"

        await interaction.response.send_message(embed=embed, ephemeral=eph)
        await interaction.followup.send(followup, ephemeral=eph)

    # Methods

    async def get_jackpot(self, server_id, action, amount):
        value = self.gambling_data["jackpot"][server_id]
        if action == "add":
            value += amount
            self.gambling_data["jackpot"][server_id] = value
        elif action == "subtract":
            jackpot = value
            self.gambling_data["jackpot"][server_id] = 500.0
            return jackpot
        elif action == "get":
            return value
    
    # Roulette

    @commands.hybrid_command(name='roulette', description='Bet your life savings away!')
    async def roulette(self, ctx, bet: int):
        if await self.check_bet_balance(ctx, bet): return
        bot_user = await self.bot.fetch_user(self.bot._application.id)
        embed = embedBuilder(bot).embed(
            color=0xffd330,
            author="Roulette",
            author_avatar=bot_user.avatar,
            description="Choose your bet",
            thumbnail="https://cdn-icons-png.flaticon.com/512/3425/3425938.png"
        )
        await ctx.send(embed=embed, view=self.RouletteView(ctx, self.bot, self.economy, self.gambling_data, bet))

    class RouletteView(ui.View):
        def __init__(self, ctx, bot, economy, gambling_data, bet, timeout=180):
            super().__init__(timeout=timeout)
            self.ctx = ctx
            self.bet = bet
            self.economy = economy
            self.bot = bot
            self.gambling_data = gambling_data['roulette']

        # Outside Bets

        @discord.ui.button(emoji="🟥", style=discord.ButtonStyle.green)
        async def red(self, interaction: discord.Interaction, button: ui.Button):
            if interaction.user.id != self.ctx.author.id: return
            num = await self.get_num(interaction)
            res = False
            if num in self.gambling_data['red']:
                res = True
            await self.send_response(self, interaction, res, num, "🟥", 1)
            
        @discord.ui.button(emoji="⬛", style=discord.ButtonStyle.green)
        async def black(self, interaction: discord.Interaction, button: ui.Button):
                if interaction.user.id != self.ctx.author.id: return
                num = await self.get_num(interaction)
                res = False
                if num in self.gambling_data['black']:
                    res = True
                await self.send_response(self, interaction, res, num, "⬛", 1)

        @discord.ui.button( label="Odd", style=discord.ButtonStyle.green)
        async def green(self, interaction: discord.Interaction, button: ui.Button):
            if interaction.user.id != self.ctx.author.id: return
            num = await self.get_num(interaction)
            res = False
            if num % 2 == 1:
                res = True
            await self.send_response(self, interaction, res, num, "Odd", 1)
        
        @discord.ui.button( label="Even", style=discord.ButtonStyle.green)
        async def even(self, interaction: discord.Interaction, button: ui.Button):
            if interaction.user.id != self.ctx.author.id: return
            num = await self.get_num(interaction)
            res = False
            if num % 2 == 0:
                res = True
            await self.send_response(self, interaction, res, num, "Even", 1)
        
        @discord.ui.button( label="High", style=discord.ButtonStyle.green)
        async def high(self, interaction: discord.Interaction, button: ui.Button):
            if interaction.user.id != self.ctx.author.id: return
            num = await self.get_num(interaction)
            res = False
            if num > 18:
                res = True
            await self.send_response(self, interaction, res, num, "High", 1)
        
        @discord.ui.button( label="Low", style=discord.ButtonStyle.green)
        async def low(self, interaction: discord.Interaction, button: ui.Button):
            if interaction.user.id != self.ctx.author.id: return
            num = await self.get_num(interaction)
            res = False
            if num <= 18:
                res = True
            await self.send_response(self, interaction, res, num, "Low", 1)
        
        @discord.ui.button( label="Dozen", style=discord.ButtonStyle.green)
        async def dozen(self, interaction: discord.Interaction, button: ui.Button):
            if interaction.user.id != self.ctx.author.id: return
            await interaction.message.delete()
            self.clear_items()
            self.add_item(self.DozenSelect(self, "Dozen", 2))
            await interaction.response.send_message(view=self)
        
        @discord.ui.button( label="Column", style=discord.ButtonStyle.green)
        async def column(self, interaction: discord.Interaction, button: ui.Button):
            if interaction.user.id != self.ctx.author.id: return
            await interaction.message.delete()
            self.clear_items()
            self.add_item(self.ColumnSelect(self, "Column", 2))
            await interaction.response.send_message(view=self)

        # Inside bets

        @discord.ui.button( label="Line (Double Street)", style=discord.ButtonStyle.red)
        async def line(self, interaction: discord.Interaction, button: ui.Button):
            if interaction.user.id != self.ctx.author.id: return
            await interaction.message.delete()
            self.clear_items()
            self.add_item(self.LineSelect(self, "Line (Double Street)", 5))
            await interaction.response.send_message(view=self)
        
        @discord.ui.button( label="Corner", style=discord.ButtonStyle.red)
        async def corner(self, interaction: discord.Interaction, button: ui.Button):
            if interaction.user.id != self.ctx.author.id: return
            await interaction.message.delete()
            self.clear_items()
            self.add_item(self.CornerSelect(self, "Corner", 8))
            await interaction.response.send_message(view=self)
        
        @discord.ui.button( label="Street", style=discord.ButtonStyle.red)
        async def street(self, interaction: discord.Interaction, button: ui.Button):
            if interaction.user.id != self.ctx.author.id: return
            await interaction.message.delete()
            self.clear_items()
            self.add_item(self.StreetSelect(self, "Street", 11))
            await interaction.response.send_message(view=self)
        
        @discord.ui.button( label="Split", style=discord.ButtonStyle.red)
        async def split(self, interaction: discord.Interaction, button: ui.Button):
            if interaction.user.id != self.ctx.author.id: return
            await interaction.response.send_modal(self.SplitSelect(self, "Split", 17))
        
        @discord.ui.button( label="Straight Up", style=discord.ButtonStyle.red)
        async def straight_up(self, interaction: discord.Interaction, button: ui.Button):
            if interaction.user.id != self.ctx.author.id: return
            await interaction.response.send_modal(self.StraightSelect(self, "Straight Up", 35))
        
        # Methods

        @staticmethod
        async def get_num(interaction):
            await interaction.response.defer(ephemeral=True, thinking=True)
            await interaction.message.delete()
            return random.randint(0, 36)
        
        @staticmethod
        async def send_response(self, interaction, res, num, bet_type, multiplier):
            if res == True:
                res = "You Win!"
                desc=f"Your winnings: **{self.bet * multiplier} {self.economy.currency}**"
                color = 0x75FF81
                await self.economy.add_money(self.bet * multiplier, interaction.guild_id, interaction.user.id)
            else:
                res = "You Lose!"
                desc = f"You lost: **{self.bet} {self.economy.currency}**"
                color = 0xed1b53
                await self.economy.subtract_money(self.bet, interaction.guild_id, interaction.user.id)

            bot_user = await self.bot.fetch_user(self.bot._application.id)
            embed = embedBuilder(self.bot).embed(
                color=color,
                author="Roulette",
                author_avatar=bot_user.avatar,
                title=res,
                description=f"The number was: {await Gambling.RouletteView.get_color(num, self.gambling_data)} **{num}**\n{desc}",
                footer=f"{bet_type} • {self.bet} • {multiplier}x"
            )
            await interaction.followup.send(embed=embed, view=Gambling.RouletteView.ForwardResult(self.ctx, embed))

        @staticmethod
        async def get_color(num, gambling_data):
            if num in gambling_data["red"]:
                color = "🟥"
            elif num in gambling_data["black"]:
                color = "⬛"
            else:
                color = "🟩"
            return color
        
        # Inner Classes

        class ForwardResult(ui.View):
            def __init__(self, ctx, embed, timeout=180):
                super().__init__(timeout=timeout)
                self.ctx = ctx
                self.embed = embed
        
            @discord.ui.button( label="Forward Result", style=discord.ButtonStyle.primary)
            async def straight_up(self, interaction: discord.Interaction, button: ui.Button):
                await interaction.response.defer()
                await interaction.edit_original_response(content="Forwarded", embed=None, view=None)
                await self.ctx.send(embed=self.embed)
        
        class DozenSelect(ui.Select):
            def __init__(self, instance, bet_type, multiplier):
                super().__init__(
                    placeholder='Pick a range',
                    options=[
                        discord.SelectOption(label='1-12', value=1),
                        discord.SelectOption(label='13-24', value=2),
                        discord.SelectOption(label='25-36', value=3)
                    ])
                self.instance = instance
                self.multiplier = multiplier
                self.bet_type = bet_type

            async def callback(self, interaction: discord.Interaction):
                num = await Gambling.RouletteView.get_num(interaction)
                res = False
                if self.values[0] == '1' and num <= 12 or self.values[0] == '2' and 13 <= num <= 24 or self.values[0] == '3' and num >= 25:
                    res = True
                await Gambling.RouletteView.send_response(self.instance, interaction, res, num, self.bet_type, self.multiplier)

        class ColumnSelect(ui.Select):
            def __init__(self, instance, bet_type, multiplier):
                super().__init__(
                    placeholder='Pick a range',
                    options=[
                        discord.SelectOption(label='1,4,7,10,13,16,19,22,25,28,31,34', value=1),
                        discord.SelectOption(label='2,5,6,8,11,14,17,20,23,26,29,32,35', value=2),
                        discord.SelectOption(label='3,6,9,12,15,18,21,24,27,30,33,36', value=3)
                    ])
                self.instance = instance
                self.multiplier = multiplier
                self.bet_type = bet_type

            async def callback(self, interaction: discord.Interaction):
                num = await Gambling.RouletteView.get_num(interaction)
                res = False
                if self.values[0] == '1' and num in [1,4,7,10,13,16,19,22,25,28,31,34] or self.values[0] == '2' and num in [2,5,6,8,11,14,17,20,23,26,29,32,35] or self.values[0] == '3' and num in [3,6,9,12,15,18,21,24,27,30,33,36]:
                    res = True
                await Gambling.RouletteView.send_response(self.instance, interaction, res, num, self.bet_type, self.multiplier)
        
        class LineSelect(ui.Select):
            def __init__(self, instance, bet_type, multiplier):
                super().__init__(
                    placeholder='Pick a range',
                    options=[
                        discord.SelectOption(label='1-6', value=1),
                        discord.SelectOption(label='7-12', value=2),
                        discord.SelectOption(label='13-18', value=3),
                        discord.SelectOption(label='19-24', value=4),
                        discord.SelectOption(label='25-30', value=5),
                        discord.SelectOption(label='31-36', value=6)
                    ])
                self.instance = instance
                self.multiplier = multiplier
                self.bet_type = bet_type

            async def callback(self, interaction: discord.Interaction):
                num = await Gambling.RouletteView.get_num(interaction)
                res = False
                if num >= int(self.values[0]) * 6 - 6 + 1 and num <= 6 * int(self.values[0]):
                    res = True
                await Gambling.RouletteView.send_response(self.instance, interaction, res, num, self.bet_type, self.multiplier)

        class CornerSelect(ui.Select):
            def __init__(self, instance, bet_type, multiplier):
                super().__init__(
                    placeholder='Pick an option',
                    options=[
                        discord.SelectOption(label='1, 2, 4, 5', value='1, 2, 4, 5'),
                        discord.SelectOption(label='2, 3, 5, 6', value='2, 3, 5, 6'),
                        discord.SelectOption(label='4, 5, 7, 8', value='4, 5, 7, 8'),
                        discord.SelectOption(label='5, 6, 8, 9', value='5, 6, 8, 9'),
                        discord.SelectOption(label='7, 8, 10, 11', value='7, 8, 10, 11'),
                        discord.SelectOption(label='8, 9, 11, 12', value='8, 9, 11, 12'),
                        discord.SelectOption(label='10, 11, 13, 14', value='10, 11, 13, 14'),
                        discord.SelectOption(label='11, 12, 14, 15', value='11, 12, 14, 15'),
                        discord.SelectOption(label='13, 14, 16, 17', value='13, 14, 16, 17'),
                        discord.SelectOption(label='14, 15, 17, 18', value='14, 15, 17, 18'),
                        discord.SelectOption(label='16, 17, 19, 20', value='16, 17, 19, 20'),
                        discord.SelectOption(label='17, 18, 20, 21', value='17, 18, 20, 21'),
                        discord.SelectOption(label='19, 20, 22, 23', value='19, 20, 22, 23'),
                        discord.SelectOption(label='20, 21, 23, 24', value='20, 21, 23, 24'),
                        discord.SelectOption(label='22, 23, 25, 26', value='22, 23, 25, 26'),
                        discord.SelectOption(label='23, 24, 26, 27', value='23, 24, 26, 27'),
                        discord.SelectOption(label='25, 26, 28, 29', value='25, 26, 28, 29'),
                        discord.SelectOption(label='26, 27, 29, 30', value='26, 27, 29, 30'),
                        discord.SelectOption(label='28, 29, 31, 32', value='28, 29, 31, 32'),
                        discord.SelectOption(label='29, 30, 32, 33', value='29, 30, 32, 33'),
                        discord.SelectOption(label='31, 32, 34, 35', value='31, 32, 34, 35'),
                        discord.SelectOption(label='32, 33, 35, 36', value='32, 33, 35, 36')
                    ])
                self.instance = instance
                self.multiplier = multiplier
                self.bet_type = bet_type
                self.corner_bets = [
                    [1, 2, 4, 5],
                    [2, 3, 5, 6],
                    [4, 5, 7, 8],
                    [5, 6, 8, 9],
                    [7, 8, 10, 11],
                    [8, 9, 11, 12],
                    [10, 11, 13, 14],
                    [11, 12, 14, 15],
                    [13, 14, 16, 17],
                    [14, 15, 17, 18],
                    [16, 17, 19, 20],
                    [17, 18, 20, 21],
                    [19, 20, 22, 23],
                    [20, 21, 23, 24],
                    [22, 23, 25, 26],
                    [23, 24, 26, 27],
                    [25, 26, 28, 29],
                    [26, 27, 29, 30],
                    [28, 29, 31, 32],
                    [29, 30, 32, 33],
                    [31, 32, 34, 35],
                    [32, 33, 35, 36]
                ]

            async def callback(self, interaction: discord.Interaction):
                num = await Gambling.RouletteView.get_num(interaction)
                res = False
                matching_corners = [corner for corner in self.corner_bets if num in corner]
                if matching_corners and str(num) in self.values[0].split(", "):
                    res = True
                await Gambling.RouletteView.send_response(self.instance, interaction, res, num, self.bet_type, self.multiplier)

        class StreetSelect(ui.Select):
            def __init__(self, instance, bet_type, multiplier):
                super().__init__(
                    placeholder='Pick a range',
                    options=[
                        discord.SelectOption(label='1-3', value=1),
                        discord.SelectOption(label='4-6', value=2),
                        discord.SelectOption(label='7-9', value=3),
                        discord.SelectOption(label='10-12', value=4),
                        discord.SelectOption(label='13-15', value=5),
                        discord.SelectOption(label='16-18', value=6),
                        discord.SelectOption(label='19-21', value=7),
                        discord.SelectOption(label='22-24', value=8),
                        discord.SelectOption(label='25-27', value=9),
                        discord.SelectOption(label='28-30', value=10),
                        discord.SelectOption(label='31-33', value=11),
                        discord.SelectOption(label='34-36', value=12)
                    ])
                self.instance = instance
                self.multiplier = multiplier
                self.bet_type = bet_type

            async def callback(self, interaction: discord.Interaction):
                num = await Gambling.RouletteView.get_num(interaction)
                res = False
                if num >= int(self.values[0]) * 3 - 3 + 1 and num <= 3 * int(self.values[0]):
                    res = True
                await Gambling.RouletteView.send_response(self.instance, interaction, res, num, self.bet_type, self.multiplier)
        
        class SplitSelect(ui.Modal):
            def __init__(self, instance, bet_type, multiplier):
                super().__init__(title="Split Bet")
                self.instance = instance
                self.multiplier = multiplier
                self.bet_type = bet_type

                self.first_number = ui.TextInput(
                    label="1st Number",
                    style=discord.TextStyle.short,
                    required=True,
                    custom_id='num1'
                )
                self.second_number = ui.TextInput(
                    label="2nd Number",
                    style=discord.TextStyle.short,
                    required=True,
                    custom_id='num2'
                )

                self.add_item(self.first_number)
                self.add_item(self.second_number)

            async def on_submit(self, interaction: discord.Interaction):
                if int(self.first_number.value) < 0 or int(self.first_number.value) > 36 or int(self.second_number.value) < 0 or int(self.second_number.value) > 36:
                    await interaction.response.send_message("Numbers can not be less than 0, or greater than 36")
                    return
                num = await Gambling.RouletteView.get_num(interaction)
                res = False
                if num == int(self.first_number.value) or num == int(self.second_number.value):
                    res = True
                await Gambling.RouletteView.send_response(self.instance, interaction, res, num, self.bet_type, self.multiplier)
        
        class StraightSelect(ui.Modal):
            def __init__(self, instance, bet_type, multiplier):
                super().__init__(title="Straight Bet")
                self.instance = instance
                self.multiplier = multiplier
                self.bet_type = bet_type

                self.number = ui.TextInput(
                    label="Number",
                    style=discord.TextStyle.short,
                    required=True,
                    custom_id='number'
                )

                self.add_item(self.number)

            async def on_submit(self, interaction: discord.Interaction):
                if int(self.number.value) < 0 or int(self.number.value) > 36:
                    await interaction.response.send_message("Number can not be less than 0, or greater than 36")
                    return
                num = await Gambling.RouletteView.get_num(interaction)
                res = False
                if num == int(self.number.value):
                    res = True
                await Gambling.RouletteView.send_response(self.instance, interaction, res, num, self.bet_type, self.multiplier)

    
    # Blackjack

    @bot.hybrid_command(name='blackjack', description='Spin to win!')
    async def blackjack(self, ctx, bet: int):
        if await self.check_bet_balance(ctx, bet): return
        await self.Blackjack(self.economy, ctx, self.bot, bet).initial_response()
    
    class Blackjack(ui.View):
        def __init__(self, economy, ctx, bot, bet, timeout=180):
            super().__init__(timeout=timeout)
            self.economy = economy
            self.ctx = ctx
            self.bot = bot
            self.bet = bet
            self.deck = {
                "clubs": ['Ace', 2, 3, 4, 5, 6, 7, 8, 9, 10, 'Jack', 'Queen', 'King'],
                "diamonds": ['Ace', 2, 3, 4, 5, 6, 7, 8, 9, 10, 'Jack', 'Queen', 'King'],
                "hearts": ['Ace', 2, 3, 4, 5, 6, 7, 8, 9, 10, 'Jack', 'Queen', 'King'],
                "spades": ['Ace', 2, 3, 4, 5, 6, 7, 8, 9, 10, 'Jack', 'Queen', 'King']
            }
            self.dealer = {}
            self.player = {}
            self.win_con_sent = False

        @discord.ui.button( label="Hit", style=discord.ButtonStyle.green, custom_id="hit")
        async def hit(self, interaction: discord.Interaction, button: ui.Button):
            await self.advance_round(interaction, self.player)

        @discord.ui.button(label="Stand", style=discord.ButtonStyle.blurple, custom_id="stand")
        async def stand(self, interaction: discord.Interaction, button: ui.Button):
            await self.disable_button("hit")
            await self.advance_round(interaction, self.dealer)

        @discord.ui.button(label="Double Down", style=discord.ButtonStyle.red, custom_id="double_down")
        async def double_down(self, interaction: discord.Interaction, button: ui.Button):
            self.bet *= 2
            await self.advance_round(interaction, self.player)
            
        # Methods

        async def initial_response(self):
            await self.draw_card(self.deck, self.dealer)
            await self.draw_card(self.deck, self.player)
            await self.draw_card(self.deck, self.player)
            bot_user = await self.bot.fetch_user(self.bot._application.id)
            embed = embedBuilder(self.bot).embed(
                    color=0xffd330,
                    author="Blackjack",
                    author_avatar=bot_user.avatar,
                    title="Choose your next move",
                    description=f"""
                    # `Dealer: {await self.calculate_score(self.dealer)}`\n
                    # {self.dealer}\n
                    # `Player: {await self.calculate_score(self.player)}`\n
                    # {self.player}
                    """,
                    footer=f"Current bet • {self.bet}"
                )
            
            await self.ctx.send(embed=embed, view=self, ephemeral=True)

        async def advance_round(self, interaction, hand):
            await interaction.response.defer()
            await self.draw_card(self.deck, hand)
            bot_user = await self.bot.fetch_user(self.bot._application.id)
            embed = embedBuilder(self.bot).embed(
                    color=0xffd330,
                    author="Blackjack",
                    author_avatar=bot_user.avatar,
                    title="Choose your next move",
                    description=f"""
                    # `Dealer: {await self.calculate_score(self.dealer)}`\n
                    # {self.dealer}\n
                    # `Player: {await self.calculate_score(self.player)}`\n
                    # {self.player}
                    """,
                    footer=f"Current bet • {self.bet}"
                )
                
            await self.check_win_con(interaction)
            await self.disable_button("double_down")
            if self.win_con_sent is False:
                await interaction.followup.send(embed=embed, view=self, ephemeral=True)

        async def check_win_con(self, interaction):
            win_con = False
            dealer_score = await self.calculate_score(self.dealer)
            dealer_cards = await self.convert_hand(self.dealer)
            dealer_blackjack = await self.check_cards(dealer_cards)

            player_score = await self.calculate_score(self.player)
            player_cards = await self.convert_hand(self.player)
            player_blackjack = await self.check_cards(player_cards)

            await interaction.edit_original_response(content="Round advanced", embed=None, view=None)

            if dealer_score > 21:
                win_con = "The dealer busted. You win!"
                color = 0x75FF81
                await self.economy.add_money(self.bet, interaction.guild_id, interaction.user.id)
            elif player_score > 21:
                win_con = "You busted."
                color = 0xed1b53
                await self.economy.subtract_money(self.bet, interaction.guild_id, interaction.user.id)
            elif player_blackjack and dealer_blackjack == False:
                win_con = "You got a blackjack!"
                color = 0x75FF81
                await self.economy.add_money(self.bet * 1.5, interaction.guild_id, interaction.user.id)
            elif dealer_blackjack and player_blackjack == False:
                win_con = "The dealer got a blackjack. You lose."
                color = 0xed1b53
                await self.economy.subtract_money(self.bet, interaction.guild_id, interaction.user.id)

            if dealer_score >= 17 and not win_con:
                if player_score == dealer_score:
                    win_con = "Nobody won. Bet returned"
                    color = 0xffd330
                elif player_score == 21:
                    win_con = "You win!"
                    color = 0x75FF81
                    await self.economy.add_money(self.bet, interaction.guild_id, interaction.user.id)
                elif dealer_score == 21:
                    win_con = "The dealer won."
                    color = 0xed1b53
                    await self.economy.subtract_money(self.bet, interaction.guild_id, interaction.user.id)
                elif player_score > dealer_score and player_score < 21:
                    win_con = "You win!"
                    color = 0x75FF81
                    await self.economy.add_money(self.bet, interaction.guild_id, interaction.user.id)
                elif dealer_score > player_score and dealer_score < 21:
                    win_con = "The dealer won."
                    color = 0xed1b53
                    await self.economy.add_money(self.bet, interaction.guild_id, interaction.user.id)
                elif player_score - 21 < dealer_score - 21:
                    win_con = "You win!"
                    color = 0x75FF81
                    await self.economy.add_money(self.bet, interaction.guild_id, interaction.user.id)
                else:
                    win_con = "Dealer wins"
                    color = 0xed1b53
                    await self.economy.subtract_money(self.bet, interaction.guild_id, interaction.user.id)
                
            if win_con is not False:
                bot_user = await self.bot.fetch_user(self.bot._application.id)
                embed = embedBuilder(self.bot).embed(
                        color=color,
                        author="Blackjack",
                        author_avatar=bot_user.avatar,
                        title=win_con,
                        description=f"""
                        # `Dealer: {dealer_score}`\n
                        # {self.dealer}\n
                        # `Player: {player_score}`\n
                        # {self.player}
                        """,
                        footer=f"Current bet • {self.bet}"
                    )
                self.win_con_sent = True
                await interaction.followup.send(embed=embed, ephemeral=True, view=Gambling.RouletteView.ForwardResult(self.ctx, embed))
                return

        async def draw_card(self, deck, hand):
            suit = random.choice(list(deck))
            card = random.choice(list(deck[suit]))
            deck[suit].remove(card)
            try:
                hand[suit].append(card)
            except KeyError:
                hand[suit] = [card]
        
        async def calculate_score(self, hand):
            score = 0
            score += sum(await self.convert_hand(hand))
            return score
        
        async def convert_hand(self, hand):
            values = []
            ace_count = 0
            for suit, cards in hand.items():
                for card in cards:
                    if card == 'Ace':
                        ace_count += 1
                        if ace_count == 1:
                            values.append(11)
                        else:
                            values.append(1)
                    elif card in ['Jack', 'Queen', 'King']:
                        values.append(10)
                    else:
                        values.append(card)
            return values
        
        async def check_cards(self, player_cards):
            return all(card in player_cards for card in [10, 11])
            
        async def disable_button(self, button):
            button = discord.utils.get(self.children, custom_id=button)
            button.disabled = True

async def setup(bot):
    await bot.add_cog(Gambling(bot))