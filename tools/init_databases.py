#! /usr/bin/env python3

from yaml import load,Loader
import sqlite3, pymysql

with open("dewey.yaml", "r") as f:
    DeweyConfig = load(stream=f, Loader=Loader)

tabletype = tuple[str, list[tuple[str, str]]]
tablestype = list[tabletype]

GachaTables: tablestype = [
    ("gacha", [
        ("maker_id",           "BIGINT"),
        ("request_message_id", "BIGINT"),
        ("id",                 "BIGINT"),
        ("accepted",           "BOOL"),
        ("name",               "varchar(256)"),
        ("description",        "varchar(256)"),
        ("rarity",             "varchar(256)"),
        ("filename",           "varchar(256)"),
    ]),
    ("gacha_user", [
        ("user_id",  "BIGINT"),
        ("last_use", "BIGINT"),
    ]),
    ("gacha_cards", [
        ("id",      "BIGINT"),
        ("card_id", "BIGINT"),
        ("user_id", "BIGINT"),
    ]),
]

CoinsTables: tablestype = [
    ("deweycoins", [
        ("uid",	            "BIGINT"),
        ("balance",	        "BIGINT"),
        ("highestbalance",	"BIGINT"),
        ("transactions",	"BIGINT"),
        ("spent",	        "BIGINT"),
        ("totalearned", 	"BIGINT"),
        ("lostgambling",    "BIGINT"),
        ("gainedgambling",  "BIGINT"),
        ("heads",           "BIGINT"),
        ("tails",           "BIGINT")
    ]),
]

ReminderTables: tablestype = [
    ("remindme", [
        ("uid",	    "BIGINT"),
        ("made",	"BIGINT"),
        ("whenr",	"BIGINT"),
        ("note",	"varchar(256)"),
        ("guild",   "BIGINT"),
        ("channel", "BIGINT"),
        ("message", "BIGINT"),
    ]),
]

SettingsTables: tablestype = [
    ("settings", [
        ("uid",              "BIGINT"),
        ("roll_reminder_dm", "bool"),
        ("roll_auto_sell",   "bool"),
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
    definitions = []

    for i in GachaTables:
        definitions.append(makeCreateStatement(table=i))
    for i in CoinsTables:
        definitions.append(makeCreateStatement(table=i))
    for i in ReminderTables:
        definitions.append(makeCreateStatement(table=i))
    for i in SettingsTables:
        definitions.append(makeCreateStatement(table=i))

    #print(definitions)

    if DeweyConfig["database-type"] == "SQLite3":
        print("creating SQLite3")
        print(f"creating new db @{DeweyConfig["dewey-sqlite-path"]}")
        
        db = sqlite3.connect(DeweyConfig["dewey-sqlite-path"])
        
        for x in definitions:
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
        print(f"creating new db @{DeweyConfig["mysql-database"]}")

        db = pymysql.connect(host=DeweyConfig["mysql-host"],
                            user=DeweyConfig["mysql-username"],
                            password=DeweyConfig['mysql-password'],
                            #database=DeweyConfig[i[0]],
                            cursorclass=pymysql.cursors.DictCursor)
        
        print("Connected to sql")

        db.cursor().execute(f'CREATE DATABASE {DeweyConfig["mysql-database"]};')
        db.cursor().execute(f'USE {DeweyConfig["mysql-database"]};')
        
        for x in definitions:
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
    else:
        raise Exception("deweyconfig database-type is not SQLite3 or MySQL")