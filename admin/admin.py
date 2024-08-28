from imports import *

@commands.has_permissions(manage_messages=True)
@bot.hybrid_command(name='purge', brief='Deletes a specified number of messages from the current channel')
async def purge(ctx, amount: int):
  await ctx.send(f'Purging messages...')
  deleted = await ctx.channel.purge(limit=amount)
  if len(deleted) == 0:
    embed = discord.Embed(title='Purge "complete"', color=0xED1B53)
    embed.description = 'No messages were deleted (bruh)'
    await ctx.send(embed=embed)
  else:
    embed = discord.Embed(title='Purge complete', color=0x75FF81)
    embed.description = f'{len(deleted)} messages were deleted'
    await ctx.send(embed=embed)