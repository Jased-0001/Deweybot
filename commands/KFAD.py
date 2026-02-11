import discord
from discord.ext import commands, tasks
import Bot
import other.Permissions as Permissions

import datetime,random



gfad_group = discord.app_commands.Group(name="gfad", description="God for a day")


@gfad_group.command(name="help", description="What is a 'god' and why for a day?")
async def gfad_help(ctx : discord.Interaction):
    if not Permissions.banned(ctx):
        await ctx.response.send_message(content="Test!", ephemeral=True)


@gfad_group.command(name="z-roll", description="! ADMIN ONLY ! Roll GOD 🎲🎲🎲🎲🎲🎲🎲🎲🎲🎲🎲🎲🎲🎲🎲🎲🎲🎲🎲")
async def gfad_roll(ctx : discord.Interaction, message_requirement:int = -1):
    if Permissions.is_override(ctx):
        if message_requirement == -1: message_requirement = Bot.DeweyConfig["kfad-must-have"]
        range_now = datetime.datetime.today()
        range_start = range_now - datetime.timedelta(weeks=1)
        range_end = range_now - datetime.timedelta(days=1)
        
        await ctx.response.defer(ephemeral=False)

        unique_authors = {}
        not_allowed = []
        qualifiers = []

        async for message in Bot.client.fetch_channel(Bot.DeweyConfig["kfad-general"]).history(limit=None, before=range_end, after=range_start): # pyright: ignore[reportOptionalMemberAccess, reportAttributeAccessIssue] # 
            #just get unique users first
            if not message.author.id in not_allowed:
                if message.author.bot: not_allowed.append(message.author.id)
                else: 
                    users_roles = [y.id for y in message.author.roles] # pyright: ignore[reportAttributeAccessIssue]
                    for i in Bot.DeweyConfig["kfad-disallowed-roles"]:
                        if i in users_roles:
                            not_allowed.append(message.author.id)

                    if not message.author.id in not_allowed:
                        if str(message.author.id) in unique_authors:
                            unique_authors[str(message.author.id)] += 1
                        else:
                            unique_authors[str(message.author.id)] = 1

        for uid,messagecount in unique_authors.items():
            if messagecount >= message_requirement:
                qualifiers.append(await ctx.guild.fetch_member(uid)) # pyright: ignore[reportOptionalMemberAccess]

        if len(qualifiers) == 0:
            await ctx.followup.send(content=f"(There aren't enough people who qualify)", silent=True, ephemeral=False)
        pick = random.choice(qualifiers)

        role = ctx.guild.get_role(Bot.DeweyConfig["kfad-role"]) # pyright: ignore[reportOptionalMemberAccess]
        for i in role.members:
            await i.remove_roles(role, reason="god for a day roll") # pyright: ignore[reportArgumentType]

        await pick.add_roles(role,reason="god got a day!!!!")

        await ctx.followup.send(content=f"{pick.mention} is the God for the Day!", silent=True, ephemeral=False)

Bot.tree.add_command(gfad_group)