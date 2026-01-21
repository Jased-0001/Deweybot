import discord
from discord.ext import commands, tasks
import Bot
import Permissions
print("La la la")

@Bot.tree.command(name="cool-command", description="echo test")
async def self(ctx : discord.Interaction, test_argument: str):
    await ctx.response.send_message(
        test_argument, ephemeral=False
    )

#@Bot.tree.command(name="requires-staff", description="permission test")
#async def self(ctx : discord.Interaction):
#    has_perms = Permissions.has_permission(ctx=ctx,allowed=["staff"])
#    print(has_perms)
#    if has_perms:
#        await ctx.response.send_message(
#            f"ok", ephemeral=False
#        )
#    else:
#        await ctx.response.send_message(
#            f"not ok :(", ephemeral=False
#        )