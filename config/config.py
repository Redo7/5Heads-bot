from imports import *

database = sqlite3.connect('config/config.db')
cursor = database.cursor()
database.execute('CREATE TABLE IF NOT EXISTS config(server_id INT, twitter_links INT DEFAULT 1, animation_3c INT DEFAULT 1)')

def update_db(server_id, feature):
    # Check db for entries
    query = 'SELECT * FROM config WHERE server_id = ?'
    data = cursor.execute(query, (server_id,)).fetchall()
    if data != [] and server_id == data[0][0]:
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
    else:
        # Create new entry if not found
        print(f"couldn't find {server_id}... Adding a new entry")
        query = 'INSERT INTO config (server_id) VALUES (?)'
        cursor.execute(query, (server_id,))
        database.commit()
        print('Database changes committed successfully')
        update_db(server_id, feature)

def check_db(server_id, feature):
    query = 'SELECT "{}" FROM config WHERE server_id = "{}"'.format(feature, server_id)
    data = cursor.execute(query).fetchall()
    return data[0][0]

@bot.hybrid_command(name="togglefeature", description="Toggles the bots features on/off")
@discord.app_commands.checks.has_permissions(administrator=True)
async def toggle_feature(ctx: commands.Context, feature) -> None:
    try:
        cursor.execute("PRAGMA table_info(config)")
        columns = [row[1] for row in cursor.fetchall()]
    except sqlite3.OperationalError:
        # Column might not exist
        columns = []
        pass

    if feature == 'server_id':
        await ctx.send("Nah uh")
        return
    if feature not in columns:
        await ctx.send(f"{feature} does not exist")
        return
    update_db(ctx.guild.id, feature)
    await ctx.send(f"Toggling {feature}")
