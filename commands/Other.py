import discord
from discord.ext import commands, tasks
import Bot
import other.Permissions as Permissions

@Bot.tree.command(name="z-repeat", description="!-ADMIN ONLY-! repeat what said :thumbs_up:")
async def self(ctx : discord.Interaction, what_said: str, channel: discord.TextChannel):
    if Permissions.is_override(ctx):
        await ctx.response.send_message(
            f"okay!", ephemeral=True
        )
        await channel.send(what_said)