from Bot import Deweybase

class Settings:
    def get_setting(self, uid:int, name:str) -> str | int | bool | None:
        try:
            return Deweybase.read_data(statement=Deweybase.create_read_statement(table="settings",values=[name],where=["uid"]),parameters=(uid,))[0][0]
        except IndexError:
            return None
    
    def set_setting(self, uid:int, name:str, value:str|int|bool):
        if self.get_setting(uid=uid,name=name) != None:
            Deweybase.write_data(statement=Deweybase.create_update_statement(table="settings",values=[name],where=["uid"]),data=(value,uid))
        else:
            Deweybase.write_data(statement=Deweybase.create_write_statement(table="settings",values=["uid",name]),data=(uid, value)) # just realized that this is propably bad