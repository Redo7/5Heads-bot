from imports import *
from config import config

@bot.hybrid_command(name='recruit', brief='Indocrinate a new member into the server')
async def recruit(ctx, amount: int):
    await ctx.send('asd')