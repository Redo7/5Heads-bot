from imports import *
from discordIntegration import *
from config import config
from typing import Optional
import uuid
from discord.ui import View, Button

database = sqlite3.connect('db/main.db')
cursor = database.cursor()
database.execute('CREATE TABLE IF NOT EXISTS voting(voting_id TEXT, msg TEXT, for TEXT, against TEXT)')

class MyView(View):
  def __init__(self, uid, timeout=None):
        super().__init__(timeout=timeout)
        self.uid = uid

  @discord.ui.button(emoji="✅", label="Vote For", style=discord.ButtonStyle.green)
  async def button_1_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
    try:
        await interaction.response.defer(ephemeral=True, thinking=True)
        data = cursor.execute('SELECT * FROM voting WHERE voting_id = ?', (self.uid,)).fetchall()
        if str(interaction.user.id) in data[0][2]:
            await interaction.followup.send("You can not vote for the same option twice")
            return
        await check_vote(interaction, self.uid, data[0][2], data[0][3], str(interaction.user.id), 'for', 'against')
    except Exception as e: print(e)
    finally:
        await interaction.followup.send("You voted for ✅")

  @discord.ui.button(emoji="✖️", label="Vote Against", style=discord.ButtonStyle.red)
  async def button_2_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
    try:
        await interaction.response.defer(ephemeral=True, thinking=True)
        data = cursor.execute('SELECT * FROM voting WHERE voting_id = ?', (self.uid,)).fetchall()
        if str(interaction.user.id) in data[0][3]:
            await interaction.followup.send("You can not vote for the same option twice")
            return
        await check_vote(interaction, self.uid, data[0][3], data[0][2], str(interaction.user.id), 'against', 'for')
    except Exception as e: print(e)
    finally:
        await interaction.followup.send("You voted against ❌")

@bot.hybrid_command(name='recruit', brief='Indocrinate a new member into the server')
async def recruit(ctx, 
name: str = commands.parameter(description="The name of the invitee"), 
avatar_link: str = commands.parameter(description="The direct link to their avatar (Right click avatar > Open image in new tab > Copy link)"),
profile_link: str = commands.parameter(description="Twitter/Social media profile link"),
additional_link: Optional[str] = commands.parameter(description="Any additional link"),
description: str = commands.parameter(description="Bio / Short description of the invitee")) -> None:
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
    embed = EmbedBuilder(
        color=0xffd330,
        author="New potential 5Head",
        thumbnail=avatar_link,
        title=name,
        description=description,
        fields=fields,
        footer=f"Voting ID: {uid}"
        )
    # Dispatch
    voting_msg = await bot.get_channel(RECRUIT_CHANNEL).send(embed=embed.build(), view=MyView(uid))
    await execute_query(f'UPDATE voting SET msg = ({voting_msg.id}) WHERE voting_id = ("{uid}")')
    await ctx.send(f"Voting posted in {bot.get_channel(RECRUIT_CHANNEL).jump_url}", ephemeral=True)

@bot.hybrid_command(name='endvoting', brief='Finalize voting by ID')
@app_commands.checks.has_permissions(manage_messages=True)
async def end_voting(ctx, uid: str):
    try:
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
        channel = bot.get_channel(ctx.channel.id) 
        message = await channel.fetch_message(message_id)
        await message.delete()
        # Delete DB entry
        await execute_query(f'DELETE FROM voting WHERE voting_id = "{uid}"')
    except discord.NotFound:
        await ctx.send(f"Message with ID {uid} not found.", ephemeral=True)
    except discord.Forbidden:
        await ctx.send("I do not have the necessary permissions to delete this message.", ephemeral=True)

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