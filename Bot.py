import io
from types import CoroutineType, FunctionType, MethodType
import discord
from discord.ext import tasks
from discord.abc import PrivateChannel
from yaml import load,Loader
import traceback
from inspect import iscoroutinefunction
from subprocess import check_output, CalledProcessError

with open("dewey.yaml", "r") as f:
    DeweyConfig = load(stream=f, Loader=Loader)


try:
    version = check_output(["git", "branch", "--show-current"]).strip() + b"-" + check_output(["git", "rev-parse", "--short", "HEAD"]).strip()
    version = version.decode()
except CalledProcessError:
    version = "unknown"

intents = discord.Intents.all()


import db_lib
Deweybase = db_lib.setup_db(name="dewey")

import other.Permissions as Permissions
import other.Settings as Settings

class botClient(discord.Client):
    def __init__(self):
        super().__init__(intents = discord.Intents.all())
        self.synced = False
        self.on_ready_functions: list[MethodType] = []
        self.on_message_functions: list[CoroutineType | FunctionType] = []

    async def on_ready(self):
        for i in self.on_ready_functions:
            if isinstance(i, (MethodType)):
                print(f" [on_ready] running on_ready_function of {i.__name__}")
                i.__call__()

        await self.wait_until_ready()
        if not self.synced:
            await tree.sync()
            self.synced = True
           
        await self.change_presence(activity=discord.Activity(name=f"Dewin' it ({version})", type=3))

        print(f" [on_ready] Dewey'd as {self.user}")


    async def on_message(self, message: discord.Message):
        for i in self.on_message_functions:
            if iscoroutinefunction(i):
                await i.__call__(message)


    async def on_raw_reaction_add(self, reactionpayload: discord.RawReactionActionEvent):
        # remove conflicting vote reactions
        if reactionpayload.channel_id == DeweyConfig["suggestions-channel"] and DeweyConfig["suggestions-enabled"]:
            if not reactionpayload.emoji.name in ["✅","❌"]: return
            assert self.user, "user is none"
            if reactionpayload.user_id == self.user.id: return
            
            reaction_channel = await client.fetch_channel(reactionpayload.channel_id)
            assert not isinstance(reaction_channel,(discord.ForumChannel,discord.CategoryChannel,PrivateChannel)), "reaction_channel assertion"
            message = await reaction_channel.fetch_message(reactionpayload.message_id)

            for i in message.reactions:
                reactors = [discord.Object(id=user.id) async for user in i.users()]
                snowflake = discord.Object(id=reactionpayload.user_id)
                
                if i.emoji == "✅" and reactionpayload.emoji.name == "❌":
                    if snowflake in reactors:
                        await message.remove_reaction(i.emoji, snowflake)
                elif i.emoji == "❌" and reactionpayload.emoji.name == "✅":
                    if snowflake in reactors:
                        await message.remove_reaction(i.emoji, snowflake)
        
        return
    
    async def on_error(self, event, error = None):
        a = traceback.format_exc()
        print(a)
        channel = await client.fetch_channel(DeweyConfig["error-channel"])
        buffer = io.BytesIO()
        buffer.write(a.encode())
        buffer.seek(0)
        assert not isinstance(channel,(discord.ForumChannel,discord.CategoryChannel,PrivateChannel)), "error channel assertion"
        await channel.send(f"<@322495136108118016> got an report for you boss (event {event})\n",file=discord.File(fp=buffer,filename="error.txt"))
        buffer.close()



client = botClient()
tree = discord.app_commands.CommandTree(client, allowed_contexts=discord.app_commands.AppCommandContext(guild=True,dm_channel=True,private_channel=True),
                                        allowed_installs=discord.app_commands.AppInstallationType(guild=True,user=True))

@tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    a = traceback.format_exc()
    print(a)
    channel = await client.fetch_channel(DeweyConfig["error-channel"])
    buffer = io.BytesIO()
    buffer.write(a.encode())
    buffer.seek(0)
    assert not isinstance(channel,(discord.ForumChannel,discord.CategoryChannel,PrivateChannel)), "error channel assertion"
    await channel.send(f"<@322495136108118016> got an report for you boss\n",file=discord.File(fp=buffer,filename="error.txt"))
    buffer.close()
    
    await interaction.followup.send(content="Ay! I gotted an error! Please ping the owners of me!")

if DeweyConfig["nick-enabled"]: import commands.Nick
if DeweyConfig["gacha-enabled"]: import commands.Gacha
if DeweyConfig["gif-enabled"]: import commands.Gif
if DeweyConfig["kfad-enabled"]: import commands.KFAD
if DeweyConfig["deweycoins-enabled"]: import commands.Bank
if DeweyConfig["obs-integration-enabled"]: import commands.OBS_Integration
import commands.Settings
import commands.Other

# RUN

client.run(token=DeweyConfig["token"])


