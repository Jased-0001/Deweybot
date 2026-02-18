import io
import discord
from discord.abc import PrivateChannel
from discord.ext import commands, tasks
import Bot
import other.Permissions as Permissions

import datetime,random



gfad_group = discord.app_commands.Group(name="gfad", description="God for a day")

async def get_qualifiers(message_requirement:int, range_start:datetime.datetime, range_end:datetime.datetime, guild:discord.Guild,getmembers:bool) -> tuple[list[discord.Member | discord.User], dict[str,int]]:
    unique_authors: dict[str, int] = {}
    not_allowed: list[int] = []
    qualifiers: list[discord.Member | discord.User] = []

    gfad_channels = Bot.DeweyConfig["kfad-channels"]
    godchannel = await Bot.client.fetch_channel(Bot.DeweyConfig["kfad-god-channel"])
    
    assert not isinstance(godchannel,(discord.ForumChannel,discord.CategoryChannel,PrivateChannel)), "god channel assertion"
    async for message in godchannel.history(limit=None, before=range_end, after=range_start):
        if not message.author.id in not_allowed:
            #not_allowed.append(message.author.id)
            pass

    for i in gfad_channels:
        cool_channel = await Bot.client.fetch_channel(i)
        assert not isinstance(cool_channel,(discord.ForumChannel,discord.CategoryChannel,PrivateChannel)), f"channel assertion '{i}' did not yeild usable channel"
        async for message in cool_channel.history(limit=None, before=range_end, after=range_start):
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
                user = guild.get_member(int(uid))
                if user == None:
                    user = await guild.fetch_member(int(uid))

                qualifiers.append(user)

    return (qualifiers, unique_authors)

@gfad_group.command(name="help", description="What is a 'god' and why for a day?")
async def gfad_help(ctx : discord.Interaction):
    if not Permissions.banned(ctx):
        await ctx.response.send_message(content="Test!", ephemeral=True)


@gfad_group.command(name="z-roll", description="! ADMIN ONLY ! Roll GOD 🎲🎲🎲🎲🎲🎲🎲🎲🎲🎲🎲🎲🎲🎲🎲🎲🎲🎲🎲")
async def gfad_roll(ctx : discord.Interaction, message_requirement:int = -1):
    if Permissions.is_override(ctx):
        if message_requirement == -1: message_requirement = Bot.DeweyConfig["kfad-must-have"]
        range_now = datetime.datetime.today()
        range_start = range_now - datetime.timedelta(weeks=1, days=1)
        range_end = range_now - datetime.timedelta(days=1)
        
        await ctx.response.defer(ephemeral=False)

        assert ctx.guild, "ctx.guild assertion"
        qualifiers, _ = await get_qualifiers(message_requirement=message_requirement, range_start=range_start, range_end=range_end,guild=ctx.guild,getmembers=True)
        print(qualifiers)

        if len(qualifiers) == 0:
            await ctx.followup.send(content=f"(There aren't enough people who qualify)", silent=True, ephemeral=False)
            return
        pick = random.choice(qualifiers)

        role = ctx.guild.get_role(Bot.DeweyConfig["kfad-role"])
        assert role, "could not find role"
        for i in role.members:
            await i.remove_roles(role, reason="god for a day roll")
        
        if type(pick) == discord.Member:
            await pick.add_roles(role,reason="god got a day!!!!")

        await ctx.followup.send(content=f"{pick.display_name} is the God for the Day (until <t:{round(range_now.timestamp())}:f>, <t:{round(range_now.timestamp())}:R>! to have a chance to be god make sure you're active in the server :) {' (please give role)' if type(pick) == discord.User else ''}", silent=True, ephemeral=False)


@gfad_group.command(name="z-get-qualifiers", description="! ADMIN ONLY ! Get people who qualify")
async def gfad_get_qualifiers(ctx : discord.Interaction, message_requirement:int = -1):
    if Permissions.is_override(ctx):
        if message_requirement == -1: message_requirement = Bot.DeweyConfig["kfad-must-have"]
        range_now = datetime.datetime.today()
        range_start = range_now - datetime.timedelta(weeks=1, days=1)
        range_end = range_now - datetime.timedelta(days=0)
        
        await ctx.response.defer(ephemeral=False)

        assert ctx.guild, "ctx.guild assertion"
        _,abcdefghijklmnopqrstuvwxyz = await get_qualifiers(message_requirement=message_requirement, range_start=range_start, range_end=range_end,guild=ctx.guild,getmembers=False)
        lalala = {}

        if len(abcdefghijklmnopqrstuvwxyz) == 0:
            await ctx.followup.send(content=f"(Nobody qualifies)", ephemeral=False)
            return
        
        for uid,messagecount in abcdefghijklmnopqrstuvwxyz.items():
            if messagecount >= message_requirement:
                lalala[str(uid)] = messagecount

        string = ""
        for uid,count in lalala.items():
            loser = await ctx.guild.fetch_member(uid)
            string += loser.name + ": " + str(count) + "\n"
        buffer = io.BytesIO()
        buffer.write(string.encode())
        buffer.seek(0)
        await ctx.followup.send(content=f"Qualifiers <t:{round(range_end.timestamp())}>",file=discord.File(fp=buffer,filename="abc.txt"))

Bot.tree.add_command(gfad_group)