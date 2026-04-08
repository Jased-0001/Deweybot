from email import message

import Bot
import db_lib
import datetime
import discord
from discord.ext import tasks

if Bot.DeweyConfig["reminders-enabled"]:
    reminders_db = db_lib.setup_db(name="remindme", file=Bot.DeweyConfig["reminders-sqlite-path"])


    #tables=["""CREATE TABLE "remindme" (
    #    "uid"	INTEGER,
    #    "made"	INTEGER,
    #    "whenr"	INTEGER,
    #    "note"	STRING,
    #    "guild" INTEGER,
    #    "channel" INTEGER,
    #    "message" INTEGER
    #)""","""
    #    CREATE TABLE "settings" (
    #        "uid"	INTEGER
    #    );"""]

    if not reminders_db:
        raise Exception("Fuck!")

    class Reminder:
        def __init__(self, uid:int, made:int, when:int, note:str, guild:int, channel:int, message:int):
            self.uid = uid
            self.made = made
            self.when = when
            self.note = note
            self.guild = guild
            self.channel = channel
            self.message = message


    def setReminder(uid: int, made: int, when: int, note: str, message: int|None,guild:int|None, channel:int|None) -> None:
        reminders_db.write_data(statement="INSERT INTO remindme (uid,made,whenr,note,message,guild,channel) VALUES (?,?,?,?,?,?,?);", data=(uid,made,when,note,message,guild,channel))
        
    def removeReminder(uid:int,when:int,made:int,messageid:int|None) -> None:
        reminders_db.write_data(statement=f"DELETE FROM remindme WHERE uid = {uid} AND whenr = {when} AND made = {made} {f"AND message = {messageid}" if messageid else ""};", data=())
        
    def getReminders(whose: None | int = None) -> list[Reminder]:
        try:
            a = reminders_db.read_data(statement=f"SELECT uid,made,whenr,note,message,guild,channel FROM remindme{" WHERE uid = (?)" if whose else ""}", parameters=(whose,) if whose else ())
            b = []

            for i in a:
                b.append(Reminder(uid=i[0],made=i[1],when=i[2],note=i[3],message=i[4],guild=i[5],channel=i[6]))

            return b
        except IndexError:
            return []
        
    @tasks.loop(name="remindme-task", minutes=1)
    async def remindme_task():
        print(" [EVIL REMINDER TASK] im runnninggg")
        reminders = getReminders()
        reminder_qualifiers:list[Reminder] = []

        timestamp = round(datetime.datetime.now().timestamp())
        for user in reminders:
            if timestamp > user.when:
                reminder_qualifiers.append(user)

        
        for i in reminder_qualifiers:
            try:
                user = Bot.client.get_user(i.uid)
                if user == None: user = await Bot.client.fetch_user(i.uid)
                dm_channel = user.dm_channel
                if not dm_channel: dm_channel = await user.create_dm()
                
                await dm_channel.send(content=f"""Hello I'm here to remind you of a thing you left on <t:{i.made}> for <t:{i.when}>{f" (https://discord.com/channels/{i.guild}/{i.channel}/{i.message})" if i.guild and i.channel and i.message else ""}
    {f"```{i.note}```" if i.note else ""}""")
            except discord.errors.Forbidden:
                pass

            #set the timeout to -2 so they don't qualify again (we don't dm them again)
            removeReminder(uid=i.uid,when=i.when,made=i.made,messageid=i.message)
    
    Bot.client.on_ready_functions.append(remindme_task.start)