from imports import *
class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

@bot.hybrid_command(name="test", description="Log message context")
async def test(ctx: commands.Context) -> None:
    print(
        ctx.args,
        ctx.author,
        ctx.bot,
        ctx.bot_permissions,
        ctx.channel,
        ctx.clean_prefix,
        ctx.cog,
        ctx.command,
        ctx.command_failed,
        ctx.current_argument,
        ctx.current_parameter,
        ctx.filesize_limit,
        ctx.guild,
        ctx.interaction,
        ctx.invoked_parents,
        ctx.invoked_subcommand,
        ctx.invoked_with,
        ctx.kwargs,
        ctx.me,
        ctx.message,
        ctx.permissions,
        ctx.prefix,
        ctx.subcommand_passed,
        ctx.valid,
        ctx.voice_client
    )
    await ctx.send("Done")

@bot.event
async def on_message(message):
    animation_3c = [':OC====3', ':C====3', '¦C===3', ':C==3', ':C=3', ':C3',
                    '¦3', ':3', '¦3', ':C3', ':C=3', '¦C3', ':C=3', ':C3', ':3']
    if ":3C====3" in message.content and message.author == bot.user:
        for frame in animation_3c:
            await message.edit(content=frame)
            time.sleep(0.4)

    if message.author == bot.user:
        return

    # if ":3" in message.content:
    #     await message.channel.send(":3C====3")

    twitter_links = ["https://x.com", "https://twitter.com"]
    for link in twitter_links:
        if message.content.startswith(link) and "/status/" in message.content:
            await message.channel.send(message.content.replace(link, "https://fxtwitter.com"))
