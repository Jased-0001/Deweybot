from discord.ext import commands
import discord
import Bot

override_users = Bot.DeweyConfig["permission-override"]

#[y.id for y in ctx.user.roles]

def banned(ctx: discord.Interaction) -> bool:
    if ctx.guild_id == None:
        return False
    
    if isinstance(ctx.user, discord.User):
        return False

    user_roles = [y.id for y in ctx.user.roles]
    for i in user_roles:
        if i == Bot.DeweyConfig["banned-role"]:
            return True
    return False

def is_override(ctx) -> bool:
    return ctx.user.id in override_users
