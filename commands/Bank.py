from random import randint

import discord
from discord.abc import PrivateChannel
from discord.ext import commands, tasks
import Bot
from moneylib.views.doors import DoorsView
import other.Permissions as Permissions
from io import BytesIO
import requests

from moneylib import *
from moneylib.views import *

# General card commands 
#######################################

coin_group = discord.app_commands.Group(name="deweycoin", description="Get rich quick using my FREE ONLINE COURSE!!!")


@coin_group.command(name="wallet", description="View your wallet!")
async def money_wallet(ctx : discord.Interaction, show: bool=True, user: discord.User | discord.Member | None = None):
    if user == None: user = ctx.user

    embed = discord.Embed(title=f"{'Your' if ctx.user.id == user.id else f'{user.display_name}\'s'} Wallet!", description="Dolla dolla, dolla dolla")
    userstuff = moneylib.getUserInfo(user=user.id)
    embed.add_field(name="Cash", value=f"D¢{userstuff.balance}")
    await ctx.response.send_message(embed=embed, ephemeral=not show)


@coin_group.command(name="stats", description="View your stats!")
async def money_stats(ctx : discord.Interaction, show: bool=True, user: discord.User | discord.Member | None = None):
    if user == None: user = ctx.user
    sayyou = user.id == ctx.user.id

    embed = discord.Embed(title=f"{'Your' if ctx.user.id == user.id else f'{user.display_name}\'s'} Stats!", description="Dolla dolla, dolla dolla")
    userstuff = moneylib.getUserInfo(user=user.id).statistics
    embed.add_field(name=f"Highest balance {'you' if sayyou else 'they'}'ve ever had", value=f"D¢{userstuff.highestbalance}")
    embed.add_field(name=f"How much total {'you' if sayyou else 'they'}'ve spent", value=f"D¢{userstuff.spent}")
    embed.add_field(name=f"How much {'you' if sayyou else 'they'}'ve earned", value=f"D¢{userstuff.totalearned}")
    embed.add_field(name=f"How many transactions {'you' if sayyou else 'they'}'ve made", value=f"{userstuff.transactions}")
    embed.add_field(name=f"How much {'you' if sayyou else 'they'}'ve lost gambling", value=f"D¢{userstuff.lostgambling}")
    embed.add_field(name=f"How many {'you' if sayyou else 'they'}'ve made while gambling", value=f"D¢{userstuff.gainedgambling}")
    embed.add_field(name=f"How many heads {'you' if sayyou else 'they'} got", value=f"D¢{userstuff.heads}")
    embed.add_field(name=f"How many tails {'you' if sayyou else 'they'} got", value=f"D¢{userstuff.tails}")
    await ctx.response.send_message(embed=embed, ephemeral=not show)


@coin_group.command(name="buy-image", description="Show an image on stream with D¢100")
async def buy_image(ctx : discord.Interaction, image : discord.Attachment):
    user = moneylib.getUserInfo(user=ctx.user.id)
    if user.balance >= 100:
        try:
            test_req = requests.get(Bot.DeweyConfig["obs-integration-post-host"] + "/test")
            print(test_req.content)
            
            if test_req.content.decode() == "hello i am dewey_obs":
                imaaage = BytesIO()
                await image.save(fp=imaaage)

                resp = requests.post(Bot.DeweyConfig["obs-integration-post-host"] + "/image",
                                    headers={"Authorization": f"Bearer {Bot.DeweyConfig["obs-integration-secret"]}"},
                                    files={"image": imaaage})
                if resp.status_code == 201:
                    await ctx.response.send_message('Successfully sent image')

                    assert Bot.client.user, "bot has no user"
                    moneylib.giveCoins(user=ctx.user.id, coins=-100)
                    moneylib.giveCoins(user=Bot.client.user.id, coins=100)
                elif resp.status_code == 401:
                    await ctx.response.send_message('Error (incorrect secret)!!!!! ' + resp.content.decode())
                elif resp.status_code == 400:
                    await ctx.response.send_message('Error (missing image)!!!!! ' + resp.content.decode())
                else:
                    await ctx.response.send_message('Error (unknown)!!!!! ' + resp.content.decode())
                
                imaaage.close()
                return
        except requests.exceptions.ConnectionError: pass
        
        await ctx.response.send_message("The server isn't running!!! your account has not been charaged")
    else:
        await ctx.response.send_message("You need D¢100 to buy these doors!")


gambling_group = discord.app_commands.Group(name="gambling", description="Get rich quick using YOUR CHILD'S COLLEGE FUND!!!!")

@gambling_group.command(name="doors", description="Gamble with 3 doors")
async def gambling_doors(ctx : discord.Interaction, bet: int):
    if ctx.guild_id != Bot.DeweyConfig["main-guild"]: 
        await ctx.response.send_message("You can only run this in the main server!!!!!", ephemeral=True)
        return
    
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



@gambling_group.command(name="coins", description="Gamble with many many many coins!")
async def gambling_coins(ctx : discord.Interaction, coins: int):
    if ctx.guild_id != Bot.DeweyConfig["main-guild"]: 
        await ctx.response.send_message("You can only run this in the main server!!!!!", ephemeral=True)
        return
    
    assert Bot.client.user, "bot has no user"

    if coins <= 0:
        await ctx.response.send_message(content=f"You can't flip no coins!",ephemeral=True)
        return

    user = moneylib.getUserInfo(user=ctx.user.id)

    if user.balance >= coins:
        moneylib.giveCoins(user=ctx.user.id, coins=-coins, doTransaction=False)
        moneylib.giveCoins(user=Bot.client.user.id, coins=coins, doTransaction=False)

        heads = 0
        tails = 0

        for i in range(coins):
            if randint(0,1) == 0: #heads
                heads += 1
            else: # tails
                tails += 1

        
        moneylib.giveCoins(user=ctx.user.id, coins=heads * 2, doTransaction=True)
        moneylib.giveCoins(user=Bot.client.user.id, coins=-heads*2, doTransaction=True)
        
        moneylib.updateValues(update=["heads"],values=[
            user.statistics.heads + heads
        ],id=ctx.user.id)
        moneylib.updateValues(update=["tails"],values=[
            user.statistics.tails + tails
        ],id=ctx.user.id)
        

        await ctx.response.send_message(content=f"You got {heads} heads/{tails} tails. so you  {heads-tails} (heads-tails) coins.")
    else:
        await ctx.response.send_message(content=f"You don't have enough coins!",ephemeral=False)




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


@coin_group.command(name="z-audit", description=" ! ADMIN ONLY ! how much money exists in the wild")
async def money_z_audit(ctx : discord.Interaction, show:bool=True):
    if Permissions.is_override(ctx):
        money = Bot.Deweybase.read_data(statement=Bot.Deweybase.create_read_statement(table="deweycoins",values=["balance"]))
        total_cash = 0

        for i in money:
            total_cash += i[0]
        
        await ctx.response.send_message(content=f"There are D¢{total_cash} in existence", ephemeral=not show)


coin_group.add_command(gambling_group)
Bot.tree.add_command(coin_group)