import discord
from discord.ext import commands, tasks
import Bot
import Permissions
import gif

@Bot.tree.command(name="house", description="house dr house md car accident funny gifs")
async def self(ctx : discord.Interaction, user: discord.Member, text: str):
    if not Permissions.banned(ctx):
        try:
            gif.gen(text)
            await ctx.response.send_message(file=discord.File('./gif/out.gif'))

        except Exception as e:
            await ctx.response.send_message(
                "Aw blast (or whatever dewey would say, i havent watched the show) i had an error", ephemeral=True
            )
            raise e
    else:
        await ctx.response.send_message(
            f"You will be destroyed for your crimes.", ephemeral=True
        )
