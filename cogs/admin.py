import discord
import sqlite3
from typing import Optional
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice
from cogs.embedBuilder import embedBuilder

import os
from dotenv import find_dotenv, load_dotenv
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
OWNER_ID = int(os.getenv('OWNER_ID'))

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', owner_id=OWNER_ID, intents=intents)

database = sqlite3.connect('db/main.db')
cursor = database.cursor()
database.execute('''
CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    server_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    message_id BIGINT NOT NULL,
    role_id BIGINT NOT NULL,
    emoji TEXT NOT NULL,
    description TEXT,
    UNIQUE(server_id, message_id, emoji)
)
''')

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.owner_id = int(os.getenv('OWNER_ID'))

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Admin cog loaded")
    
    def is_admin(interaction: discord.Interaction) -> bool:
        return interaction.user.guild_permissions.administrator

    @bot.hybrid_command(name='purge', description='Deletes a specified number of messages from the current channel')
    @app_commands.describe(amount="The amount of messages to delete")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int):
        await ctx.send(f'Purging messages...')
        deleted = await ctx.channel.purge(limit=amount+1)
        if len(deleted) == 0:
            embed = embedBuilder(self.bot).embed(
                color = "#ED1B53",
                author = 'Purge "complete"',
                description = 'No messages were deleted (bruh)'
                )
            await ctx.send(embed=embed)
        else:
            embed = embedBuilder(self.bot).embed(
                color = "#75FF81",
                author = 'Purge complete',
                description = f'{len(deleted)} messages were deleted'
                )
            await ctx.send(embed=embed)

    @commands.hybrid_command(name="safepurge", description="Reply to a message to delete everything after it")
    @commands.has_permissions(manage_messages=True)
    async def safe_purge(self, ctx):
        if ctx.interaction is not None:
            await ctx.send("This command must be invoked with `!safepurge`")
            return
        if ctx.message.reference:
            try:
                reply_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            except discord.NotFound:
                await ctx.send("Could not find the message.")
                return

            count = 0
            async for message in ctx.channel.history(limit=None, after=reply_message):
                count += 1
            await self.purge(ctx, count + 1)
        else:
            await ctx.send("This command must be used as a reply to a message.")
    
    @bot.hybrid_command(name="createreactionrole", description="Create a reaction role message")
    @app_commands.describe(channel="The channel to send the message in", role="The role to assign", emoji="The emoji to use as a reaction", description="Used for database lookup for certain features")
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.check(is_admin)
    async def createreactionrole(self, ctx: commands.Context, channel: discord.TextChannel, role: discord.Role, emoji: str, description: Optional[str]):
        if not ctx.guild.me.guild_permissions.manage_roles:
            raise ValueError("Missing permission to manage roles.")

        if role.position >= ctx.guild.me.top_role.position:
            raise ValueError("Can not assign a role because it's higher than the bot's highest role.")

        message = await channel.send(f"React with {emoji} to get the {role.mention} role")
        await message.add_reaction(emoji)

        cursor.execute('''
            INSERT INTO roles (server_id, channel_id, message_id, role_id, emoji, description)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (ctx.guild.id, channel.id, message.id, role.id, str(emoji), description))
        database.commit()

        embed = embedBuilder(bot).embed(
                color="#ffd330",
                author="Role assignment",
                author_avatar=self.bot.user.avatar,
                description=f"Reaction role message created in {channel.mention}"
            )
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        await self.fetch_role_action("add", payload)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        await self.fetch_role_action("remove", payload)

    async def fetch_role_action(self, action, payload):
        data = cursor.execute('''
                SELECT role_id FROM roles
                WHERE server_id = ? AND message_id = ? AND emoji = ?
        ''', (payload.guild_id, payload.message_id, str(payload.emoji))).fetchone()
        if data:
            role_id = data[0]
            guild = self.bot.get_guild(payload.guild_id)
            role = guild.get_role(role_id)
            member = guild.get_member(payload.user_id)
            if member is None:
                member = await guild.fetch_member(payload.user_id)
            if not role or not member: return
            if action == "add":
                await member.add_roles(role)
            elif action == "remove":
                await member.remove_roles(role)
                

async def setup(bot):
    await bot.add_cog(Admin(bot))