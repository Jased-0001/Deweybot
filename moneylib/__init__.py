import db_lib,Bot
import discord

import moneylib.types

money_database = db_lib.setup_db(name="deweycoins", tables=["""CREATE TABLE "deweycoins" (
	"uid"	INTEGER,
	"balance"	INTEGER,
	"highestbalance"	INTEGER,
	"transactions"	INTEGER,
	"spent"	INTEGER,
	"totalearned"	INTEGER
);""",], file=Bot.DeweyConfig["deweycoins-sqlite-path"])

print(money_database)
if not money_database:
    raise Exception("Fuck!")


def updateValues(update:list[str],values:list[str | int],id:int) -> None:
    assert len(update) == len(values)
    for i in range(len(update)):
        money_database.write_data(statement=
                                  f"UPDATE deweycoins SET {update[i]}=? WHERE uid = (?)", data=(values[i],id))

def getUserInfo(user: int | discord.Member | discord.User) -> moneylib.types.User:
    if type(user) == discord.Member or type(user) == discord.User:
        user = user.id
    a = money_database.read_data(statement="SELECT uid,balance,highestbalance,transactions,spent,totalearned FROM deweycoins WHERE uid = (?)", parameters=(user,))[0]
    return moneylib.types.User(uid=a[0],balance=a[1],statistics=moneylib.types.Statistics(
        highestbalance=a[2],transactions=a[3],spent=a[4],totalearned=a[5]
    ))

def giveCoins(user: int | discord.Member | discord.User, coins:int, doTransaction:bool=True) -> None:
    if type(user) == discord.Member or type(user) == discord.User:
        user = user.id

    coinuser = getUserInfo(user=user)

    coinuser.balance += coins
    coinuser.statistics.transactions += 1 if doTransaction else 0

    if coins < 0: # took away coins
        coinuser.statistics.spent -= coins
    elif coins > 0: # gave coins
        coinuser.statistics.totalearned += coins
        if coinuser.statistics.highestbalance < coinuser.balance:
            coinuser.statistics.highestbalance = coinuser.balance
    print(coinuser)
    updateValues(update=["balance","highestbalance","transactions","totalearned","spent"],
                 values=[coinuser.balance,coinuser.statistics.highestbalance
                  ,coinuser.statistics.transactions, coinuser.statistics.totalearned
                  ,coinuser.statistics.spent],id=coinuser.uid)
