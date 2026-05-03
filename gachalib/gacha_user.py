import gachalib, gachalib.types
from Bot import Deweybase

from time import time

def get_everyone_with_timeouts() -> list[gachalib.types.GachaUser]:
    a = Deweybase.read_data(statement=Deweybase.create_read_statement(table="gacha_user", values=["user_id", "last_use"]))
    b = []

    for user in a:
        b.append(gachalib.types.GachaUser(user_id=user[0], last_use=user[1]))
        
    return b

def get_user_timeout(user_id:int) -> gachalib.types.GachaUser:
    a = Deweybase.read_data(statement=Deweybase.create_read_statement(table="gacha_user", values=["last_use"], where=["user_id"]), parameters=(user_id,))

    if len(a) == 0:
        return gachalib.types.GachaUser(user_id=user_id,last_use=-1)
    else:
        return gachalib.types.GachaUser(user_id=user_id,last_use=a[0][0])
    

def set_user_timeout(user_id:int,unix_time:int) -> gachalib.types.GachaUser: #also update
    if get_user_timeout(user_id=user_id).last_use == -1:
        Deweybase.write_data(statement=Deweybase.create_write_statement(table="gacha_user", values=["user_id", "last_use"]), data=(user_id,unix_time))
    else:
        Deweybase.write_data(statement=Deweybase.create_update_statement(table="gacha_user",values=["last_use"],where=["user_id"]), data=(unix_time,user_id))
        
    return gachalib.types.GachaUser(user_id=user_id,last_use=unix_time)


def get_timestamp() -> int:
    return round(time())