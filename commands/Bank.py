import discord
from discord.abc import PrivateChannel
from discord.ext import commands, tasks
import Bot
from moneylib.views.doors import DoorsView
import other.Permissions as Permissions

from moneylib import *
from moneylib.views import *

# General card commands 
#######################################

coin_group = discord.app_commands.Group(name="deweycoin", description="Get rich quick using my FREE ONLINE COURSE!!!")


@coin_group.command(name="wallet", description="View your wallet!")
async def money_wallet(ctx : discord.Interaction, show: bool=True, user: discord.User | discord.Member | None = None):
    if user == None: user = ctx.user

    embed = discord.Embed(title="Wallet!", description="Dolla dolla, dolla dolla")
    userstuff = moneylib.getUserInfo(user=user.id)
    embed.add_field(name="Cash", value=f"D¢{userstuff.balance}")
    await ctx.response.send_message(embed=embed, ephemeral=not show)


@coin_group.command(name="stats", description="View your stats!")
async def money_stats(ctx : discord.Interaction, show: bool=True, user: discord.User | discord.Member | None = None):
    if user == None: user = ctx.user
    sayyou = user.id == ctx.user.id

    embed = discord.Embed(title="Stats!", description="Dolla dolla, dolla dolla")
    userstuff = moneylib.getUserInfo(user=user.id).statistics
    embed.add_field(name=f"Highest balance {'you' if sayyou else 'they'}'ve ever had", value=f"D¢{userstuff.highestbalance}")
    embed.add_field(name=f"How much total {'you' if sayyou else 'they'}'ve spent", value=f"D¢{userstuff.spent}")
    embed.add_field(name=f"How much {'you' if sayyou else 'they'}'ve earned", value=f"D¢{userstuff.totalearned}")
    embed.add_field(name=f"How many transactions {'you' if sayyou else 'they'}'ve made", value=f"{userstuff.transactions}")
    embed.add_field(name=f"How much {'you' if sayyou else 'they'}'ve lost gambling", value=f"D¢{userstuff.lostgambling}")
    embed.add_field(name=f"How many {'you' if sayyou else 'they'}'ve made while gambling", value=f"D¢{userstuff.gainedgambling}")
    await ctx.response.send_message(embed=embed, ephemeral=not show)





gambling_group = discord.app_commands.Group(name="gambling", description="Get rich quick using YOUR CHILD'S COLLEGE FUND!!!!")

@gambling_group.command(name="doors", description="Gamble with 3 doors")
async def gambling_doors(ctx : discord.Interaction, bet: int):
    assert Bot.client.user, "bot has no user"

    if bet <= 0 or bet == 1:
        await ctx.response.send_message(content=f"You can't bet nothing/that little",ephemeral=True)
        return

    user = moneylib.getUserInfo(user=ctx.user.id)

    if user.balance >= bet:
        user.balance -= bet
        moneylib.giveCoins(user=ctx.user.id, coins=-bet)
        moneylib.giveCoins(user=Bot.client.user.id, coins=bet)

        view = DoorsView(message=ctx, bet=bet)
        await ctx.response.send_message(embed=view.mkembed(),view=view)
    else:
        await ctx.response.send_message(content=f"You don't have enough!",ephemeral=False)








@coin_group.command(name="givecoins", description="Give coins to someone else")
async def money_give_coin(ctx : discord.Interaction, user: discord.Member | discord.User, coins:int):
    if user == None: user = ctx.user
    if coins <= 0:
        await ctx.response.send_message(content=f"You can't give no money!",ephemeral=True)
        return


    us = moneylib.getUserInfo(ctx.user.id)
    other = moneylib.getUserInfo(user.id)

    if us.balance >= coins:
        us.balance -= coins
        other.balance += coins
        moneylib.giveCoins(user=ctx.user.id, coins=-coins)
        moneylib.giveCoins(user=user.id, coins=coins)
        await ctx.response.send_message(content=f"Okay! You now have {us.balance}, and they have {other.balance}",ephemeral=False)
    else:
        await ctx.response.send_message(content=f"You don't have enough!",ephemeral=False)

@coin_group.command(name="z-movecoins", description=" ! ADMIN ONLY ! force move coins from user -> user (ex. take from dewey) (allows debt)")
async def gacha_z_move_coin(ctx : discord.Interaction, from_user:discord.Member | discord.User, to_user: discord.Member | discord.User | None, coins:int):
    if Permissions.is_override(ctx):
        if to_user == None: to_user = ctx.user
        moneylib.giveCoins(from_user.id, -coins)
        moneylib.giveCoins(to_user.id, coins)
        await ctx.response.send_message("ok",ephemeral=True)

@coin_group.command(name="z-givecoins", description=" ! ADMIN ONLY ! materialize coins (i advice against doing this)")
async def money_z_give_coin(ctx : discord.Interaction, user: discord.Member | discord.User | None, coins:int):
    if Permissions.is_override(ctx):
        if user == None: user = ctx.user
        moneylib.giveCoins(user.id, coins)
        await ctx.response.send_message("ok",ephemeral=True)

coin_group.add_command(gambling_group)
Bot.tree.add_command(coin_group)