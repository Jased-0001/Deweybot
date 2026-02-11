import io
import discord
from discord.ext import commands, tasks
import Bot
import other.Permissions as Permissions

import datetime,random



gfad_group = discord.app_commands.Group(name="gfad", description="God for a day")

async def get_qualifiers(message_requirement:int, range_start:datetime.datetime, range_end:datetime.datetime, guild:discord.Guild,getmembers:bool) -> tuple[list[discord.Member], list[dict[int,int]]]:
    unique_authors = {}
    not_allowed = []
    qualifiers = []

    genchannel = await Bot.client.fetch_channel(Bot.DeweyConfig["kfad-general"])

    async for message in genchannel.history(limit=None, before=range_end, after=range_start): # pyright: ignore[reportOptionalMemberAccess, reportAttributeAccessIssue] # 
        #just get unique users first
        if not message.author.id in not_allowed:
            if message.author.bot: not_allowed.append(message.author.id)
            else: 
                if type(message.author) == discord.Member:
                    users_roles = [y.id for y in message.author.roles]
                    for i in Bot.DeweyConfig["kfad-disallowed-roles"]:
                        if i in users_roles:
                            not_allowed.append(message.author.id)

                    if not message.author.id in not_allowed:
                        if str(message.author.id) in unique_authors:
                            unique_authors[str(message.author.id)] += 1
                        else:
                            unique_authors[str(message.author.id)] = 1
                else:
                    not_allowed.append(message.author.id)

    if getmembers:
        for uid,messagecount in unique_authors.items():
            if messagecount >= message_requirement:
                user = guild.get_member(uid)
                if user == None:
                    user = await guild.fetch_member(uid)

                qualifiers.append(user)

    return (qualifiers, unique_authors) # pyright: ignore[reportReturnType]

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

        qualifiers, _ = await get_qualifiers(message_requirement=message_requirement, range_start=range_start, range_end=range_end,guild=ctx.guild,getmembers=True) # pyright: ignore[reportArgumentType]
        

        if len(qualifiers) == 0:
            await ctx.followup.send(content=f"(There aren't enough people who qualify)", silent=True, ephemeral=False)
            return
        pick = random.choice(qualifiers)

        role = ctx.guild.get_role(Bot.DeweyConfig["kfad-role"]) # pyright: ignore[reportOptionalMemberAccess]
        for i in role.members: # pyright: ignore[reportOptionalMemberAccess]
            await i.remove_roles(role, reason="god for a day roll") # pyright: ignore[reportArgumentType]

        await pick.add_roles(role,reason="god got a day!!!!") # pyright: ignore[reportArgumentType]

        await ctx.followup.send(content=f"{pick.mention} is the God for the Day!", silent=True, ephemeral=False)


@gfad_group.command(name="z-get-qualifiers", description="! ADMIN ONLY ! Get people who qualify")
async def gfad_get_qualifiers(ctx : discord.Interaction, message_requirement:int = -1):
    if Permissions.is_override(ctx):
        if message_requirement == -1: message_requirement = Bot.DeweyConfig["kfad-must-have"]
        range_now = datetime.datetime.today()
        range_start = range_now - datetime.timedelta(weeks=1)
        range_end = range_now - datetime.timedelta(days=1)
        
        await ctx.response.defer(ephemeral=False)

        _,abcdefghijklmnopqrstuvwxyz = await get_qualifiers(message_requirement=message_requirement, range_start=range_start, range_end=range_end,guild=ctx.guild,getmembers=False) # pyright: ignore[reportArgumentType]
        lalala = {}

        if len(abcdefghijklmnopqrstuvwxyz) == 0:
            await ctx.followup.send(content=f"(Nobody qualifies)", ephemeral=False)
            return
        
        for uid,messagecount in abcdefghijklmnopqrstuvwxyz.items():
            if messagecount >= message_requirement:
                lalala[str(uid)] = messagecount

        string = ""
        for uid,count in lalala.items(): # pyright: ignore[reportAttributeAccessIssue]
            loser = await ctx.guild.fetch_member(uid) # pyright: ignore[reportOptionalMemberAccess]
            string += loser.name + ": " + str(count) + "\n" # pyright: ignore[reportOptionalMemberAccess]
        buffer = io.BytesIO()
        buffer.write(string.encode())
        buffer.seek(0)
        await ctx.followup.send(content=f"Qualifiers",file=discord.File(fp=buffer,filename="abc.txt"))

Bot.tree.add_command(gfad_group)