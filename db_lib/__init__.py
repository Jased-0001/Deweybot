import sqlite3
from typing import Any

database = None
database_path = "./dewey.db"

def init_db():
    global database
    database = sqlite3.connect(database_path)
    try:
        database.cursor().execute("CREATE TABLE gacha \
(maker_id int(19), request_message_id int(20), id int(5), accepted bool(1), name varchar(256), description varchar(256), rarity varchar(256), filename varchar(256));")
    except sqlite3.OperationalError as e:
        msg = str(e)
        if msg.startswith("table ") and msg.endswith(" already exists"):
            print(" [SQL] Tables already exist")
        else:
            raise e
    
    database.commit()

def get_db() -> sqlite3.Connection:
    global database
    if database is None:
        database = sqlite3.connect(database_path)
    return database

def write_data(statement: str, data: tuple[Any]):
    get_db().cursor().execute(statement, data)
    get_db().commit()

def read_data(statement: str, parameters: tuple[Any]) -> list[Any]:
    return get_db().cursor().execute(statement, parameters).fetchall()

def close_connection(exception):
    global database
    if database is not None:
        database.close()