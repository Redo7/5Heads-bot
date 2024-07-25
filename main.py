from imports import *

TOKEN = os.getenv('TOKEN')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.hybrid_command(name="sync", description="Syncs commands",hidden=True)
async def sync(ctx):
    if str(ctx.author.id) == OWNER_ID:
        resp = await bot.tree.sync()
        await ctx.send(f"Syncing {len(resp)} commands.")
    else:
        await ctx.send('Nah uh')

if __name__ == "__main__":
    bot.run(TOKEN)
