import discord
#from discord.ext import commands, tasks
from yaml import load,Loader

with open("dewey.yaml", "r") as f:
    DeweyConfig = load(stream=f, Loader=Loader)

import Permissions#, db_lib


intents = discord.Intents.default()

#db_lib.init_db()

class botClient(discord.Client):
    def __init__(self):
        super().__init__(intents = discord.Intents.all())
        self.synced = False
    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync()
            self.synced = True
           
        await self.change_presence(activity=discord.Activity(name="Dewin' it", type=3))

        print(f"Dewey'd as {self.user}")
    #async def on_message(self, message):
    #    if message.author == self.user:
    #        return


client = botClient()
tree = discord.app_commands.CommandTree(client)

import commands.Nick
import commands.Gif

# RUN

client.run(token=DeweyConfig["token"])


