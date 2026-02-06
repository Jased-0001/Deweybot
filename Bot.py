import discord
#from discord.ext import commands, tasks
from discord import emoji
from discord import reaction
from yaml import load,Loader
import traceback

with open("dewey.yaml", "r") as f:
    DeweyConfig = load(stream=f, Loader=Loader)

import other.Permissions as Permissions
import db_lib
from subprocess import check_output, CalledProcessError

try:
    version = check_output(["git", "branch", "--show-current"]).strip() + b"-" + check_output(["git", "rev-parse", "--short", "HEAD"]).strip()
    version = version.decode()
except CalledProcessError:
    version = "unknown"

intents = discord.Intents.default()

db_lib.init_db()

class botClient(discord.Client):
    def __init__(self):
        super().__init__(intents = discord.Intents.all())
        self.synced = False
    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync()
            self.synced = True
           
        await self.change_presence(activity=discord.Activity(name=f"Dewin' it ({version})", type=3))

        print(f"Dewey'd as {self.user}")
    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return
        if message.channel.id == DeweyConfig["suggestions-channel"]:
            await message.add_reaction("✅")
            await message.add_reaction("❌")
        return
        #print(message.author.name + " - " + message.content)


client = botClient()
tree = discord.app_commands.CommandTree(client)

@tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    channel = await client.fetch_channel(DeweyConfig["error-channel"])
    await channel.send(f"<@322495136108118016> got an report for you boss\n```{traceback.format_exc()}```") # pyright: ignore[reportAttributeAccessIssue]
    
    await interaction.response.send_message("Ay! I gotted an error! Please ping the owners of me!")

import commands.Nick
import commands.Other
import commands.Gacha
import commands.Gif

# RUN

client.run(token=DeweyConfig["token"])


