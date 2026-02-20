import discord
from discord.ext import commands, tasks
import Bot
import other.Permissions as Permissions
import gif

@Bot.tree.command(name="house", description="house dr house md car accident funny gifs")
@discord.app_commands.allowed_installs(guilds=True, users=True)
async def house(ctx : discord.Interaction, text: str):
    if not Permissions.banned(ctx):
        await ctx.response.defer()
        
        image_file = discord.File(gif.gen(text),filename=f"{text.replace(" ", "_")[0:32]}.gif")
        await ctx.followup.send(file=image_file)
    else:
        await ctx.response.send_message(
            f"You will be destroyed for your crimes.", ephemeral=True
        )
