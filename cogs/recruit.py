import os
import json
import uuid
import sqlite3
import discord
from cogs import config
from cogs.discordIntegration import discordIntegration
from cogs.embedBuilder import embedBuilder
from typing import Optional
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button

from dotenv import find_dotenv, load_dotenv
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

OWNER_ID = os.getenv('OWNER_ID')
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
bot = commands.Bot(command_prefix='!', owner_id=OWNER_ID, intents=intents)

RECRUIT_CHANNEL = int(os.getenv('RECRUIT_CHANNEL'))
database = sqlite3.connect('db/main.db')
cursor = database.cursor()
database.execute('CREATE TABLE IF NOT EXISTS voting(voting_id TEXT, msg TEXT, for TEXT, against TEXT)')

class Recruit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.recruit_channel = None


    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Recruit cog loaded")
        self.recruit_channel = self.bot.get_channel(int(os.getenv('RECRUIT_CHANNEL'))) 
        if self.recruit_channel is None:
            print(f"Error: Could not find channel with ID: {RECRUIT_CHANNEL}")

    # Initial Command
    @bot.hybrid_command(name='recruit', description='Indocrinate a new member into the server')
    @app_commands.describe(name="The name of the invitee")
    @app_commands.describe(avatar_link="The direct link to their avatar (Right click avatar > Open image in new tab > Copy link)")
    @app_commands.describe(profile_link="Twitter/Social media profile link")
    @app_commands.describe(additional_link="Any additional link")
    @app_commands.describe(description="Bio / Short description of the invitee")
    async def recruit(self, ctx, name: str, avatar_link: str, profile_link: str, additional_link: str, description: str) -> None:
        # Prep DB
        uid = str(uuid.uuid4())
        print(f'Creating new database entry for voting {uid}')
        await execute_query(f'INSERT INTO voting (voting_id) VALUES ("{uid}")')
        cursor.execute('UPDATE voting SET for = (?) WHERE voting_id = (?)', (json.dumps([]), uid))
        cursor.execute('UPDATE voting SET against = (?) WHERE voting_id = (?)', (json.dumps([]), uid))
        database.commit()
        # Prep Embed
        fields = [{"name": "Profile Link", "value": profile_link, "inline": False}]
        if additional_link != None:
            fields = [{"name": "Profile Link", "value": profile_link, "inline": False}, {"name": "Additional Link", "value": additional_link, "inline": False}]
        embed = embedBuilder(self.bot).embed(
            color="#ffd330",
            author="New potential 5Head",
            thumbnail=avatar_link,
            title=name,
            description=description,
            fields=fields,
            footer=f"Voting ID: {uid}"
            )
        try:
            # Dispatch
            data = cursor.execute('SELECT role_id FROM roles WHERE server_id = ? AND description = ?', (ctx.guild.id, "recruit")).fetchone()
            if data:
                guild = self.bot.get_guild(ctx.guild.id)
                role = guild.get_role(data[0])
                voting_msg = await self.recruit_channel.send(f"{role.mention}", embed=embed, view=RecruitView(uid))
            else: 
                voting_msg = await self.recruit_channel.send(embed=embed, view=RecruitView(uid))
            await execute_query(f'UPDATE voting SET msg = ({voting_msg.id}) WHERE voting_id = ("{uid}")')
            await ctx.send(f"Voting posted in {self.recruit_channel.jump_url}", ephemeral=True)
        except Exception:
            raise ValueError("Error occurred during dispatch")

    # End Voting Command
    @bot.hybrid_command(name='endvoting', description='Finalize voting by ID')
    @app_commands.describe(uid="Unique ID assigned to the voting. Visible in the embed's footer")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def end_voting(self, ctx, uid: str):
        try:
            # Search DB
            query = 'SELECT * FROM voting WHERE voting_id = ?'
            data = cursor.execute(query, (uid,)).fetchall()
            message_id = data[0][1]
            votes_for = len(json.loads(data[0][2]))
            votes_against = len(json.loads(data[0][3]))
            # Check for voting verdict
            if votes_for == votes_against:
                verdict = f"The votes are even (✅ {votes_for}:{votes_against} ❌). Cannot resolve the voting without a majority vote."
                await ctx.send(verdict)
                return
            verdict = f"The final vote for voting `{uid}` was: ✅ {votes_for}:{votes_against} ❌"
            await ctx.send(verdict)
            # Delete discord message
            channel = self.recruit_channel
            message = await channel.fetch_message(message_id)
            await message.delete()
            # Delete DB entry
            await execute_query(f'DELETE FROM voting WHERE voting_id = "{uid}"')
        except discord.NotFound:
            raise ValueError(f"Message with ID {uid} not found.")
        except discord.Forbidden:
            raise ValueError("Missing permission to delete this message.")

# View Setup
class RecruitView(View):
    def __init__(self, uid, timeout=None):
        super().__init__(timeout=timeout)
        self.uid = uid

    @discord.ui.button(emoji="✅", label="Vote For", style=discord.ButtonStyle.green)
    async def vote_for(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.defer(ephemeral=True, thinking=True)
            data = cursor.execute('SELECT * FROM voting WHERE voting_id = ?', (self.uid,)).fetchall()
            if str(interaction.user.id) in data[0][2]:
                await interaction.followup.send("You can not vote for the same option twice")
                return
            await check_vote(interaction, self.uid, data[0][2], data[0][3], str(interaction.user.id), 'for', 'against')
            await interaction.followup.send("You voted for ✅")
        except Exception as e: print(e)

    @discord.ui.button(emoji="✖️", label="Vote Against", style=discord.ButtonStyle.red)
    async def vote_against(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.defer(ephemeral=True, thinking=True)
            data = cursor.execute('SELECT * FROM voting WHERE voting_id = ?', (self.uid,)).fetchall()
            if str(interaction.user.id) in data[0][3]:
                await interaction.followup.send("You can not vote for the same option twice")
                return
            await check_vote(interaction, self.uid, data[0][3], data[0][2], str(interaction.user.id), 'against', 'for')
            await interaction.followup.send("You voted against ❌")
        except Exception as e: print(e)

async def check_vote(interaction, vote_id, check_for, check_against, user_id, db_for, db_against):
    if user_id in check_against:
        votes_against = json.loads(check_against)
        votes_against.remove(user_id)
        cursor.execute(f"UPDATE voting SET {db_against} = (?) WHERE voting_id = (?)", (json.dumps(votes_against), vote_id,))
        database.commit()
    votes = json.loads(check_for)
    votes.append(user_id)
    cursor.execute(f"UPDATE voting SET {db_for} = (?) WHERE voting_id = (?)", (json.dumps(votes), vote_id,))
    database.commit()

async def execute_query(query):
    cursor.execute(query)
    database.commit()

async def setup(bot):
    await bot.add_cog(Recruit(bot))