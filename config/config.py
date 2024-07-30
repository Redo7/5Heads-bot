from discord.app_commands import Choice

from imports import *

database = sqlite3.connect('config/config.db')
cursor = database.cursor()
database.execute('CREATE TABLE IF NOT EXISTS config(server_id INT, twitter_links INT DEFAULT 1, animation_3c INT DEFAULT 1)')

@bot.event
async def on_guild_join(guild):
    query = 'SELECT * FROM config WHERE server_id = ?'
    data = cursor.execute(query, (guild.id,)).fetchall()   
    if data != [] and guild.id == data[0][0]:
        print(f'Joined "{guild}" ({guild.id}), but found an existing database entry. Skipping...')
        return
    else:
        print(f'Creating new database entry for "{guild}" ({guild.id})')
        query = 'INSERT INTO config (server_id) VALUES (?)'
        cursor.execute(query, (guild.id,))
        database.commit()

def update_db(server_id, feature):
    # Check db for entries
    query = 'SELECT * FROM config WHERE server_id = ?'
    data = cursor.execute(query, (server_id,)).fetchall()
    # Get value
    query = 'SELECT "{}" FROM config WHERE server_id = ?'.format(feature)
    current_state = cursor.execute(query, (server_id,)).fetchall()
    # Flip value
    current_state = current_state[0][0]
    current_state ^= 1
    # Set new value
    query = 'UPDATE config SET "{}" = ? WHERE server_id = ?'.format(feature)
    cursor.execute(query, (current_state, server_id))
    database.commit()
    print(f'Database changes: ({feature}: {current_state}) for server: {server_id} committed successfully')
    return current_state

def check_db(server_id, feature):
    query = 'SELECT "{}" FROM config WHERE server_id = "{}"'.format(feature, server_id)
    data = cursor.execute(query).fetchall()
    return data[0][0]


@bot.hybrid_command(name="togglefeature", description="Toggles the bots features on/off")
@app_commands.choices(choices=[
        Choice(name=":3c Animation", value="animation_3c"),
        Choice(name="FXTwitter", value="twitter_links")
        ])
@app_commands.checks.has_permissions(administrator=True)
async def toggle_feature(ctx: commands.Context, choices: Choice[str]) -> None:
    status = update_db(ctx.guild.id, choices.value)
    status = 'enabled' if status == 1 else 'disabled'
    await ctx.send(f"{choices.name} is now {status}")
