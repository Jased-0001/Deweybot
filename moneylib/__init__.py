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

def getUserInfo(user: int | discord.Member | discord.User) -> moneylib.types.User:
    if type(user) == discord.Member or type(user) == discord.User:
        user = user.id
    a = money_database.read_data(statement="SELECT uid,balance,highestbalance,transactions,spent,totalearned FROM deweycoins WHERE uid = (?)", parameters=(user,))[0]
    return moneylib.types.User(uid=a[0],balance=a[1],statistics=moneylib.types.Statistics(
        highestbalance=a[2],transactions=a[3],spent=a[4],totalearned=a[5]
    ))
print(getUserInfo(user=322495136108118016))