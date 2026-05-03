import db_lib,Bot
import discord

import moneylib.types



def register_user(user: int) -> moneylib.types.User:
    Bot.Deweybase.write_data(statement=Bot.Deweybase.create_write_statement(table="deweycoins",
    values=["uid","balance","highestbalance","transactions","spent","totalearned","lostgambling","gainedgambling","heads","tails"]),
    data=(user,0,0,0,0,0,0,0,0,0))
    return moneylib.types.User(uid=user)

def updateValues(update:list[str],values:list[str | int],id:int) -> None: # TODO: update this because it probably doesn't need a weird for loop anymore
    assert len(update) == len(values)
    for i in range(len(update)):
        Bot.Deweybase.write_data(statement=Bot.Deweybase.create_update_statement(table="deweycoins",
        values=[update[i]],
        where=["uid"]),
        data=(values[i],id))

def getUserInfo(user: int) -> moneylib.types.User:
    try:
        a = Bot.Deweybase.read_data(statement=Bot.Deweybase.create_read_statement(table="deweycoins",
        values=["uid","balance","highestbalance","transactions","spent","totalearned","lostgambling","gainedgambling","heads","tails"],
        where=["uid"]),
        parameters=(user,))[0]
        if len(a) == 0: raise IndexError("user not in the thing")
        return moneylib.types.User(uid=a[0],balance=a[1],statistics=moneylib.types.Statistics(
            highestbalance=a[2],transactions=a[3],spent=a[4],totalearned=a[5],lostgambling=a[6],gainedgambling=a[7],heads=a[8],tails=a[9]
        ))
    except IndexError:
        return register_user(user=user)

def giveCoins(user: int, coins:int, doTransaction:bool=True) -> None:
    coinuser = getUserInfo(user=user)

    coinuser.balance += coins
    coinuser.statistics.transactions += 1 if doTransaction else 0

    if coins < 0 and doTransaction: # took away coins
        coinuser.statistics.spent -= coins
    elif coins > 0 and doTransaction: # gave coins
        coinuser.statistics.totalearned += coins
        if coinuser.statistics.highestbalance < coinuser.balance:
            coinuser.statistics.highestbalance = coinuser.balance

    updateValues(update=["balance","highestbalance","transactions","totalearned","spent"],
                 values=[coinuser.balance,coinuser.statistics.highestbalance
                  ,coinuser.statistics.transactions, coinuser.statistics.totalearned
                  ,coinuser.statistics.spent],id=coinuser.uid)
