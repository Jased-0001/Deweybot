import gachalib, gachalib.types

from time import time

def get_everyone_with_timeouts() -> list[gachalib.types.GachaUser]:
    a = gachalib.gacha_database.read_data("SELECT user_id,last_use FROM gacha_user")
    b = []

    for user in a:
        b.append(gachalib.types.GachaUser(user_id=user[0], last_use=user[1]))
        
    return b

def get_user_timeout(user_id:int) -> gachalib.types.GachaUser:
    a = gachalib.gacha_database.read_data(f"SELECT last_use FROM gacha_user WHERE (user_id) = (?)", (user_id,))

    if len(a) == 0:
        return gachalib.types.GachaUser(user_id=user_id,last_use=-1)
    else:
        return gachalib.types.GachaUser(user_id=user_id,last_use=a[0][0])
    

def set_user_timeout(user_id:int,unix_time:int) -> gachalib.types.GachaUser: #also update
    if get_user_timeout(user_id=user_id).last_use == -1:
        gachalib.gacha_database.write_data("INSERT INTO gacha_user (user_id,last_use) VALUES (?,?)", (user_id,unix_time))
    else:
        gachalib.gacha_database.write_data("UPDATE gacha_user SET last_use=? WHERE user_id=?", (unix_time,user_id))
        
    return gachalib.types.GachaUser(user_id=user_id,last_use=unix_time)


def get_timestamp() -> int:
    return round(time())