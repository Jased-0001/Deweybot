from discord.ext import commands
import discord
import Bot

overrides = Bot.DeweyConfig["permission-override"]
override_users = []
override_roles = []


repeat = Bot.DeweyConfig["dewey-repeat-allowed"]
repeat_users = []
repeat_roles = []

for i in overrides:
    if i[0] == "role":
        override_roles.append(i[1])
    elif i[0] == "member":
        override_users.append(i[1])
    else:
        raise Exception(i[0], "is not 'role' or 'member' (check permission-override)")

for i in repeat:
    if i[0] == "role":
        repeat_roles.append(i[1])
    elif i[0] == "member":
        repeat_users.append(i[1])
    else:
        raise Exception(i[0], "is not 'role' or 'member' (check dewey-repeat-allowed)")


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

def is_override(ctx: discord.Interaction) -> bool:
    if ctx.user.id in override_users:
        return True
    
    if type(ctx.user) == discord.Member:
        user_roles = [y.id for y in ctx.user.roles]
        for i in user_roles:
            if i in override_roles:
                return True
            
    return False

def is_repeat(ctx: discord.Interaction) -> bool:
    if ctx.user.id in repeat_users:
        return True
    
    if type(ctx.user) == discord.Member:
        user_roles = [y.id for y in ctx.user.roles]
        for i in user_roles:
            if i in repeat_roles:
                return True
            
    return False
