from imports import *

if not os.path.isfile('config/config.json'):
    with open("config/config.json", "w") as file:
        file.write('{}')
        file.close()
        print('Created configuration file.')
config_data = open('config/config.json')
config = json.load(config_data)

@bot.hybrid_command(name="togglefeature", description="Toggles the bots features on/off")
@discord.app_commands.checks.has_permissions(administrator=True)
async def toggle_feature(ctx: commands.Context, feature) -> None:
    await ctx.send(f"Toggling {feature}")
