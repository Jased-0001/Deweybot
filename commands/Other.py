import discord
from discord.ext import commands, tasks
import Bot
import other.Permissions as Permissions

#@Bot.tree.command(name="nickname", description="Change someone's nickname")
#async def self(ctx : discord.Interaction, user: discord.Member, nickname: str):
#    if not Permissions.banned(ctx):
#        try:
#            previous = user.nick
#            await user.edit(nick=nickname)
#            await ctx.response.send_message(
#                f"<:Dewey:1463436505849528425> Dewey blast! <:Dewey:1463436505849528425> (name changed `{previous}` -> `{nickname}`)", ephemeral=False
#            )
#        except Exception as e:
#            await ctx.response.send_message(
#                "Aw blast (or whatever dewey would say, i havent watched the show) i had an error", ephemeral=True
#            )
#            raise e
#    else:
#        await ctx.response.send_message(
#            f"You will be destroyed for your crimes.", ephemeral=True
#        )