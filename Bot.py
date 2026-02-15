import io
import discord
#from discord.ext import commands, tasks
from discord.abc import PrivateChannel
from yaml import load,Loader
import traceback

with open("dewey.yaml", "r") as f:
    DeweyConfig = load(stream=f, Loader=Loader)

import other.Permissions as Permissions
from subprocess import check_output, CalledProcessError


try:
    version = check_output(["git", "branch", "--show-current"]).strip() + b"-" + check_output(["git", "rev-parse", "--short", "HEAD"]).strip()
    version = version.decode()
except CalledProcessError:
    version = "unknown"

intents = discord.Intents.all()

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
        if message.channel.id == DeweyConfig["suggestions-channel"] and not message.content.startswith("!") and DeweyConfig["suggestions-enabled"]:
            await message.add_reaction("✅")
            await message.add_reaction("❌")
        return
        #print(message.author.name + " - " + message.content)
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
    
    async def on_error(self, event, error):
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
tree = discord.app_commands.CommandTree(client, allowed_installs=discord.app_commands.AppInstallationType(guild=True,user=True))

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
import commands.Other

# RUN

client.run(token=DeweyConfig["token"])


