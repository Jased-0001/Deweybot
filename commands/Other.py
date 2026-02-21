import discord
from discord.ext import commands, tasks
import Bot
import other.Permissions as Permissions

@Bot.tree.command(name="z-repeat", description="!-ADMIN ONLY-! repeat what said :thumbs_up:")
@discord.app_commands.allowed_installs(guilds=True, users=False)
async def adminrepeat(ctx : discord.Interaction, what_said: str, channel: discord.TextChannel | discord.Thread):
    if Permissions.is_override(ctx):
        await ctx.response.send_message(
            f"okay!", ephemeral=True
        )
        await channel.send(what_said)

@Bot.tree.command(name="version", description="What version am I?")
@discord.app_commands.allowed_installs(guilds=True, users=False)
async def version(ctx : discord.Interaction):
    await ctx.response.send_message(
        f"Yo yo yo man, its the big dewbert!\n{Bot.version}", ephemeral=True
    )

@Bot.tree.command(name="sexer", description="Sexer")
@discord.app_commands.allowed_installs(guilds=True, users=True)
async def sexer(ctx : discord.Interaction):
    sexer = open("other/ytp_sexer.mp4", "rb")
    await ctx.response.send_message(file=discord.File(fp=sexer, filename="sexer.mp4"))
    sexer.close()