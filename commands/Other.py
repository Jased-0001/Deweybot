import discord
from discord.ext import commands, tasks
import Bot
import other.Permissions as Permissions


admin_group = discord.app_commands.Group(name="z-admin-other", description="g")

if Bot.DeweyConfig["reminders-enabled"]:
    import other.Remindme as Remindme

    
    @Bot.tree.command(name="remindme", description="Get a DM after X amount of time !")
    async def remindme(ctx : discord.Interaction, weeks:int=0, days:int=0, hours:int=0, minutes:int=0, note: str = ""):
        if weeks == 0 and days == 0 and hours == 0 and minutes == 0:
            await ctx.response.send_message("you have to select a time", ephemeral=True)
        if len(note) > 256:
            await ctx.response.send_message("you should shorten your note")

        now = Remindme.datetime.datetime.today()
        delta = Remindme.datetime.timedelta(weeks=weeks, days=days, hours=hours, minutes=minutes)
        when = round((now+delta).timestamp())

        message = await ctx.response.send_message("I'll dm you on " + str(now+delta) + f" (<t:{when}>) ")
        
        Remindme.setReminder(uid=ctx.user.id,made=round(now.timestamp()),when=when,note=note,message=message.message_id,guild=ctx.guild_id,channel=ctx.channel_id)
        Remindme.getReminders()





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