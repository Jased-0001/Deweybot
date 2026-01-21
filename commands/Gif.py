import discord
from discord.ext import commands, tasks
import Bot
import Permissions
import gif

@Bot.tree.command(name="house", description="house dr house md car accident funny gifs")
async def self(ctx : discord.Interaction, text: str):
    if not Permissions.banned(ctx):
        await ctx.response.defer()
        try:
            image_file = discord.File(gif.gen(text),filename=f"haus.gif")
            await ctx.followup.send(file=image_file)

        except Exception as e:
            await ctx.followup.send(
                "Aw blast (or whatever dewey would say, i havent watched the show) i had an error", ephemeral=True
            )
            raise e
    else:
        await ctx.response.send_message(
            f"You will be destroyed for your crimes.", ephemeral=True
        )
