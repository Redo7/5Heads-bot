from imports import *
from discordIntegration import *
from config import config
from typing import Optional
from discord.ui import View, Button

class MyView(View):
  @discord.ui.button(emoji="✅", label="Vote For", style=discord.ButtonStyle.green)
  async def button_1_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.response.send_message("Green!", ephemeral=True)

  @discord.ui.button(emoji="✖️", label="Vote Against", style=discord.ButtonStyle.red)
  async def button_2_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.response.send_message("Red :(", ephemeral=True)

@bot.hybrid_command(name='recruit', brief='Indocrinate a new member into the server')
async def recruit(ctx, 
                    name: str = commands.parameter(description="The name of the invitee"), 
                    avatar_link: str = commands.parameter(description="The direct link to their avatar (Right click avatar > Open image in new tab > Copy link)"),
                    profile_link: str = commands.parameter(description="Twitter/Social media profile link"),
                    additional_link: Optional[str] = commands.parameter(description="Any additional link"),
                    description: str = commands.parameter(description="Bio / Short description of the invitee")) -> None:
    embed = EmbedBuilder(
        color=0xffd330,
        author="New potential 5Head",
        thumbnail=avatar_link,
        title=name,
        description=description,
        fields=[{"name": "Profile Link", "value": profile_link, "inline": False}, {"name": "Additional Link", "value": additional_link, "inline": False}]
        )
    
    await bot.get_channel(RECRUIT_CHANNEL).send(embed=embed.build(), view=MyView())
    await ctx.send(f"Voting posted in {bot.get_channel(RECRUIT_CHANNEL).jump_url}", ephemeral=True)