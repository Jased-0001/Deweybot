import discord
from discord.ext import commands, tasks
from discord import app_commands

#import db_lib
import Permissions

intents = discord.Intents.default()

#db_lib.init_db()

class botClient(discord.Client):
    def __init__(self):
        super().__init__(intents = discord.Intents.all())
        self.synced = False
    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            print("Not synced")
            await tree.sync()
            print("Synced now")

            self.synced = True
           
        await self.change_presence(activity=discord.Activity(name="Dewey", type=3))

        print(f"Logged in as {self.user}")
    #async def on_message(self, message):
    #    if message.author == self.user:
    #        return


client = botClient()
tree = app_commands.CommandTree(client)

import commands.Nick
import commands.Gif

# RUN

tokenfile = open("token", "r")
token = tokenfile.read()
tokenfile.close()

client.run(token=token)


