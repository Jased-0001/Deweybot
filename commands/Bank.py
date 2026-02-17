import discord
from discord.abc import PrivateChannel
from discord.ext import commands, tasks
import Bot
import other.Permissions as Permissions

from moneylib import *

# General card commands 
#######################################

coin_group = discord.app_commands.Group(name="deweycoin", description="Get rich quick using my FREE ONLINE COURSE!!!")


@coin_group.command(name="wallet", description="View your wallet!")
async def gacha_wallet(ctx : discord.Interaction, show: bool=True):
    embed = discord.Embed(title="Wallet!", description="Dolla dolla, dolla dolla")
    userstuff = moneylib.getUserInfo(ctx.user)
    embed.add_field(name="Cash", value=f"D¢{userstuff.balance}")
    await ctx.response.send_message(embed=embed)


@coin_group.command(name="stats", description="View your stats!")
async def gacha_stats(ctx : discord.Interaction, show: bool=True):
    embed = discord.Embed(title="Stats!", description="Dolla dolla, dolla dolla")
    userstuff = moneylib.getUserInfo(ctx.user).statistics
    embed.add_field(name="Highest balance you've ever had", value=f"D¢{userstuff.highestbalance}")
    embed.add_field(name="How much total you've spent", value=f"D¢{userstuff.spent}")
    embed.add_field(name="How much you've earned", value=f"D¢{userstuff.totalearned}")
    embed.add_field(name="How many transactions you've made", value=f"{userstuff.transactions}")
    await ctx.response.send_message(embed=embed)

@coin_group.command(name="z-givecoins", description=" ! ADMIN ONLY ! give coins")
async def gacha_give_coin(ctx : discord.Interaction, user: discord.Member | discord.User | None, coins:int):
    if user == None: user = ctx.user
    moneylib.giveCoins(user, coins)
    await ctx.response.send_message("ok",ephemeral=True)

Bot.tree.add_command(coin_group)