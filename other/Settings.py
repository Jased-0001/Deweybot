import db_lib

class Settings:
    def __init__(self,db_ident:str):
        self.database = db_lib.get_db(name=db_ident)
    
    def get_setting(self, uid:int, name:str) -> str | int | bool | None:
        assert self.database, f"db not open"
        try:
            return self.database.read_data(statement=f"SELECT {name} FROM settings WHERE uid = ?", parameters=(uid,))[0][0]
        except IndexError:
            return None
    
    def set_setting(self, uid:int, name:str, value:str|int|bool):
        assert self.database, f"db not open"
        if self.get_setting(uid=uid,name=name):
            self.database.write_data(statement=f"UPDATE settings SET {name}=? WHERE uid = ?", data=(value,uid)) # UPDATE gacha SET {update}=? WHERE id=?;
        else:
            self.database.write_data(statement=f"INSERT INTO settings (uid, {name}) VALUES (?,?)", data=(uid,value)) # just realized that this is propably bad