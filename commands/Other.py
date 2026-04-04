import discord
from discord.ext import commands, tasks
import Bot
import other.Permissions as Permissions
import random
import re


admin_group = discord.app_commands.Group(name="z-admin-other", description="g")

if Bot.DeweyConfig["reminders-enabled"]:
    import other.Remindme as Remindme

    
    @Bot.tree.command(name="remindme", description="Get a DM after X amount of time !")
    async def remindme(ctx : discord.Interaction, weeks:int=0, days:int=0, hours:int=0, minutes:int=0, note: str = ""):
        if weeks == 0 and days == 0 and hours == 0 and minutes == 0:
            await ctx.response.send_message("you have to select a time", ephemeral=True)
            return
        if len(note) > 256:
            await ctx.response.send_message("you should shorten your note")
            return

        now = Remindme.datetime.datetime.today()
        delta = Remindme.datetime.timedelta(weeks=weeks, days=days, hours=hours, minutes=minutes)
        when = round((now+delta).timestamp())

        message = await ctx.response.send_message("I'll dm you on " + str(now+delta) + f" (<t:{when}>) ")
        
        Remindme.setReminder(uid=ctx.user.id,made=round(now.timestamp()),when=when,note=note,message=message.message_id,guild=ctx.guild_id,channel=ctx.channel_id)
        Remindme.getReminders()

responses = [
    "It is certain", "Reply hazy, try again", "Don't count on it",
    "It is decidedly so", "Ask again later", "My reply is no",
    "Without a doubt", "Better not tell you now", "My sources say no",
    "Yes definitely", "Cannot predict now", "Outlook not so good",
    "You may rely on it", "Concentrate and ask again", "Very doubtful",
    "As I see it, yes",
    "Most likely",
    "Outlook good",
    "Yes",
    "Signs point to yes"
]


@Bot.client.event
async def on_message(message: discord.Message):
    if Bot.DeweyConfig["grok-responses"]:
        assert Bot.client.user
        if re.search(f"(@?grok|@?gork|{Bot.client.user.mention}) (am|is|are)", message.content.lower()):
            if random.random() < 0.02:
                await message.reply("oh poor baby 🥺🥺 do you need the robot to make you pictures? 🥺🥺 yeah? 🥺🥺 do you need the bo-bot to write you essay too? yeah ??? you can't do it?? 🥺🥺 you're a moron??🥺🥺 do you need chat gpt to fuck your wife ?? 🥺🥺🥺")
            else:
                await message.reply(random.choice(responses))
            return
    if Bot.DeweyConfig["suggestions-enabled"]:
        if message.author == Bot.client.user:
            pass
        if message.channel.id == Bot.DeweyConfig["suggestions-channel"] and not message.content.startswith("!"):
            await message.add_reaction("✅")
            await message.add_reaction("❌")
        return


@admin_group.command(name="repeat", description="!-ADMIN ONLY-! repeat what said :thumbs_up:")
@discord.app_commands.allowed_installs(guilds=True, users=False)
async def adminrepeat(ctx : discord.Interaction, what_said: str, channel: discord.TextChannel | discord.Thread, reply: str = "0"):
    if Permissions.is_override(ctx):
        if reply == "0":
            await channel.send(content=what_said)
        else:
            reply_int = int(reply)
            reply_message = await channel.fetch_message(reply_int)
            await reply_message.reply(content=what_said)

        await ctx.response.send_message(
            f"okay!", ephemeral=True
        )

if Bot.DeweyConfig["gacha-enabled"]:
    import gachalib
    if Bot.DeweyConfig["gacha-reminder-task"]:
        @admin_group.command(name="start-reminder-task", description="!-ADMIN ONLY-! restart reminder task")
        @discord.app_commands.allowed_installs(guilds=True, users=False)
        async def reminder_task(ctx : discord.Interaction):
            if Permissions.is_override(ctx):
                if not gachalib.reminder_task.is_running():
                    gachalib.reminder_task.start()
                    await ctx.response.send_message(
                        f"okay!", ephemeral=True
                    )
                else:
                    await ctx.response.send_message(
                        f"its running already", ephemeral=True
                    )
        @admin_group.command(name="check-reminder-task", description="!-ADMIN ONLY-! check if reminder task running")
        @discord.app_commands.allowed_installs(guilds=True, users=False)
        async def check_reminder_task(ctx : discord.Interaction):
            if Permissions.is_override(ctx):
                await ctx.response.send_message(
                    gachalib.reminder_task.is_running(), ephemeral=True
                )


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

Bot.tree.add_command(admin_group)
