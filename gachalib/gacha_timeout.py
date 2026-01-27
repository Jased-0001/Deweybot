import gachalib, gachalib.types, db_lib

from time import time

def get_user_timeout(user_id:int) -> gachalib.types.Cards_Timeout:
    a = db_lib.read_data(f"SELECT last_use FROM gacha_user WHERE (user_id) = (?)", (user_id,))

    if len(a) == 0:
        return gachalib.types.Cards_Timeout(user_id=user_id,last_use=-1)
    else:
        return gachalib.types.Cards_Timeout(user_id=user_id,last_use=a[0][0])
    

def set_user_timeout(user_id:int,unix_time:int) -> gachalib.types.Cards_Timeout: #also update
    if get_user_timeout(user_id=user_id).last_use == -1:
        db_lib.write_data("INSERT INTO gacha_user (user_id,last_use) VALUES (?,?)", (user_id,unix_time))
    else:
        db_lib.write_data("UPDATE gacha_user SET last_use=? WHERE user_id=?", (unix_time,user_id))
        
    return gachalib.types.Cards_Timeout(user_id=user_id,last_use=unix_time)


def get_timestamp() -> int:
    return round(time())