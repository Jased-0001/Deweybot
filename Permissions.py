from discord.ext import commands

override_users = [
    322495136108118016, # JASE
    940684920966250567,  # jinxxxddd_
]

#[y.id for y in ctx.user.roles]

def banned(ctx):
    user_roles = [y.id for y in ctx.user.roles] # pyright: ignore[reportAttributeAccessIssue]
    for i in user_roles:
        if i == 1463430130167709804:
            return True
    return False

#def has_permission(ctx: commands.Context[commands.Bot]):#, allowed: list):
#    if ctx.user.id in override_users: return True # pyright: ignore[reportAttributeAccessIssue]
#    #print([y.id for y in ctx.user.roles])
#    user_roles = [y.id for y in ctx.user.roles] # pyright: ignore[reportAttributeAccessIssue]
#    #for i in allowed:
#    #    if ranks[i] in user_roles: # pyright: ignore[reportUndefinedVariable]
#    #        return True
#    return False