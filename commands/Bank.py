import discord
from discord.abc import PrivateChannel
from discord.ext import commands, tasks
import Bot
import other.Permissions as Permissions

from moneylib import *

# General card commands 
#######################################

gacha_group = discord.app_commands.Group(name="deweycoin", description="Get rich quick using my FREE COURSE!!!")

Bot.tree.add_command(gacha_group)