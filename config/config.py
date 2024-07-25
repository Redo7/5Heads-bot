from imports import *

database = sqlite3.connect('config/config.db')
cursor = database.cursor()
database.execute('CREATE TABLE IF NOT EXISTS config(server_id INT, disabled_features STRING)')

def db_test(server_id, content):
    query = 'SELECT * FROM config'
    data = cursor.execute(query).fetchall()

    # Find a query to skim the database for server_id
    # If found -> Iterate until entry matches the server_id -> commit changes
    # else -> make a new one

    for entry in data:
        if server_id == entry[0]:
            # Update
            print(f'found {server_id} in {entry}')
        else:
            # Write New
            print(f"couldn't find {server_id}... Adding a new entry")
            query = 'INSERT INTO config VALUES (?, ?)'
            cursor.execute(query, (server_id, content))
            database.commit()
            print('database changes committed successfully')

db_test(123495681, 'someFunction')

@bot.hybrid_command(name="togglefeature", description="Toggles the bots features on/off")
@discord.app_commands.checks.has_permissions(administrator=True)
async def toggle_feature(ctx: commands.Context, feature) -> None:
    await ctx.send(f"Toggling {feature}")
