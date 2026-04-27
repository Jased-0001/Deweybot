#! /usr/bin/env python3

#raise Exception("NOT WRITTEN YET!!!!!!!!!!!! come back later :)")

from yaml import load,Loader
import sqlite3, pymysql

with open("dewey.yaml", "r") as f:
    DeweyConfig = load(stream=f, Loader=Loader)

tabletype = tuple[str, list[tuple[str, str]]]
tablestype = list[tabletype]

GachaTables: tablestype = [
    ("gacha", [
        ("maker_id",           "int(19)"),
        ("request_message_id", "int(20)"),
        ("id",                 "int(5)"),
        ("accepted",           "BOOL"),
        ("name",               "varchar(256)"),
        ("description",        "varchar(256)"),
        ("rarity",             "varchar(256)"),
        ("filename",           "varchar(256)"),
    ]),
    ("gacha_user", [
        ("user_id",  "int(19)"),
        ("last_use", "int(20)"),
    ]),
    ("gacha_cards", [
        ("id",      "int(20)"),
        ("card_id", "int(5)"),
        ("user_id", "int(19)"),
    ]),
    ("settings", [
        ("uid",              "int(19)"),
        ("roll_reminder_dm", "bool"),
        ("roll_auto_sell",   "bool"),
    ]),
]

CoinsTables: tablestype = [
    ("deweycoins", [
        ("uid",	            "INTEGER"),
        ("balance",	        "INTEGER"),
        ("highestbalance",	"INTEGER"),
        ("transactions",	"INTEGER"),
        ("spent",	        "INTEGER"),
        ("totalearned", 	"INTEGER"),
        ("lostgambling",    "INTEGER"),
        ("gainedgambling",  "INTEGER"),
        ("heads",           "INTEGER"),
        ("tails",           "INTEGER")
    ]),
    ("settings", [
        ("uid",              "INTEGER"),
    ]),
]

ReminderTables: tablestype = [
    ("remindme", [
        ("uid",	    "INTEGER"),
        ("made",	"INTEGER"),
        ("whenr",	"INTEGER"),
        ("note",	"varchar(256)"),
        ("guild",   "INTEGER"),
        ("channel", "INTEGER"),
        ("message", "INTEGER"),
    ]),
    ("settings", [
        ("uid",              "INTEGER"),
    ]),
]

def makeCreateStatement(table:tabletype) -> str:
    fields = ""

    for i in range(len(table[1])):
        # create '"name" TYPE,'
        fields += f" {table[1][i][0]} {table[1][i][1]}{',' if not i+1==len(table[1]) else ''}\n"

    definition = f"CREATE TABLE {table[0]} (\n{fields});"

    return definition

if __name__ == "__main__":
    print("Yo yo yo! Welcome to the Dewey Database maker")

    #gacha_database = db_lib.setup_db(name="gacha", file=Bot.DeweyConfig["gacha-sqlite-path"])
    gachadefinitions =    []
    coinsdefinitions =    []
    reminderdefinitions = []

    for i in GachaTables:
        gachadefinitions.append(makeCreateStatement(table=i))
    for i in CoinsTables:
        coinsdefinitions.append(makeCreateStatement(table=i))
    for i in ReminderTables:
        reminderdefinitions.append(makeCreateStatement(table=i))

    if DeweyConfig["database-type"] == "SQLite3":
        print("creating SQLite3")
        dbs:list[tuple[str,list]] = [
            ("gacha-sqlite-path",gachadefinitions),
            ("deweycoins-sqlite-path",coinsdefinitions),
            ("reminders-sqlite-path",reminderdefinitions),
            ]
        for i in dbs:
            print(f"creating new db @{DeweyConfig[i[0]]}")

            db = sqlite3.connect(DeweyConfig[i[0]])
            
            for x in i[1]:
                try:
                    db.cursor().execute(x)
                except sqlite3.OperationalError as e:
                    msg = str(e)
                    if msg.startswith("table ") and msg.endswith(" already exists"):
                        print("already exists")
                        pass
                    else:
                        raise e

            db.commit()
            db.close()
            print("closed")
    elif DeweyConfig["database-type"] == "MySQL":
        print("creating MySQL")
        dbs:list[tuple[str,list]] = [
            ("mysql-gacha-database",gachadefinitions),
            ("mysql-deweycoins-database",coinsdefinitions),
            ("mysql-reminders-database",reminderdefinitions),
            ]
        for i in dbs:
            print(f"creating new db @{DeweyConfig[i[0]]}")

            db = pymysql.connect(host=DeweyConfig["mysql-host"],
                                user=DeweyConfig["mysql-username"],
                                password=DeweyConfig['mysql-password'],
                                #database=DeweyConfig[i[0]],
                                cursorclass=pymysql.cursors.DictCursor)
            print("Connected to sql")
            
            db.cursor().execute(f'CREATE DATABASE {DeweyConfig[i[0]]};')
            db.cursor().execute(f'USE {DeweyConfig[i[0]]};')

            for x in i[1]:
                db.cursor().execute(x)

            db.commit()
            db.close()
            print("closed")
    else:
        raise Exception("deweyconfig database-type is not SQLite3 or MySQL")