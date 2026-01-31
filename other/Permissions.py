from discord.ext import commands
import discord
import Bot

override_users = Bot.DeweyConfig["permission-override"]

#[y.id for y in ctx.user.roles]

def banned(ctx: discord.Interaction) -> bool:
    #if ctx.guild == False:
    #    return True
    #else:
    #    user_roles = [y.id for y in ctx.user.roles] # pyright: ignore[reportAttributeAccessIssue]
    #    for i in user_roles:
    #        if i == Bot.DeweyConfig["banned-role"]:
    #            return True
    #    return False
    return False

def is_override(ctx) -> bool:
    return ctx.user.id in override_users


#def has_permission(ctx: commands.Context[commands.Bot]):#, allowed: list):
#    if ctx.user.id in override_users: return True # pyright: ignore[reportAttributeAccessIssue]
#    #print([y.id for y in ctx.user.roles])
#    user_roles = [y.id for y in ctx.user.roles] # pyright: ignore[reportAttributeAccessIssue]
#    #for i in allowed:
#    #    if ranks[i] in user_roles: # pyright: ignore[reportUndefinedVariable]
#    #        return True
#    return False