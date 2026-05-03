import sqlite3
import pymysql
import Bot

OpenDatabases = {}

class BaseDatabase:
    def __init__(self,ident: str, database_path: str, connect: bool = True, verbose: bool = True) -> None:
        self.ident: str = ident
        self.database_path: str = database_path
        #self.tables: list[str] | None = tables
        self.type: str = ""

        self.database: sqlite3.Connection | pymysql.Connection | None = None
        self.cursor: sqlite3.Cursor | pymysql.cursors.Cursor | None = None

        self.verbose: bool = verbose

        if connect: 
            self.connect()

        print(f" [db_lib] [{self.ident}] opened db '{self.database_path}' ({"connected" if connect else "not connected"})")
    
    def connect(self) -> None:
        pass

    def create_write_statement(self,table:str,values:list[str]) -> str:
        return ""
    
    def create_update_statement(self,table:str,values:list[str], where:list[str]=[]) -> str:
        return ""
    
    def create_delete_statement(self,table:str, where:list[str]=[]) -> str:
        return ""

    def create_read_statement(self,table:str,values:list[str], where:list[str]=[]) -> str:
        return ""
    
    def write_data(self, statement: str, data: tuple) -> None:
        if self.database and self.cursor:
            if self.verbose: print(f" [{self.type}] [{self.ident}] write '{statement}' , '{data}")
            self.cursor.execute(statement, data)
            self.database.commit()
        else:
            raise Exception("database was not connected")
    
    def read_data(self, statement: str, parameters: tuple = ()) -> list | tuple:
        if self.database and self.cursor:
            if self.verbose: print(f" [{self.type}] [{self.ident}] read '{statement}' , '{parameters}")
            self.cursor.execute(statement, parameters)
            a = self.cursor.fetchall()
            print(a)
            return a
        else:
            raise Exception("database was not connected")
    
    def close_connection(self):
        if self.database is not None:
            self.database.close()

    def __repr__(self) -> str:
        return f"(DB '{self.ident}'@'{self.database_path}' ({'connected' if self.database else 'not connected'}{', verbose' if self.verbose else ''}))"

class SQLite3Database(BaseDatabase):
    def __init__(self, ident: str, database_path: str, connect: bool = True, verbose: bool = True) -> None:
        super().__init__(ident=ident, database_path=database_path, connect=connect, verbose=verbose)
        self.type = "SQLite3"
        return

    def create_write_statement(self,table:str,values:list[str]) -> str:
        return f"INSERT INTO {table} ({",".join(values)}) VALUES ({",".join(["?" for i in range(len(values))])})"
    
    def create_update_statement(self,table:str,values:list[str], where:list[str]=[]) -> str:
        return f"UPDATE {table} SET{",".join([" " + i + "=?" for i in values])}{" WHERE" + " AND ".join([" " + i + "=?" for i in where])}"
    
    def create_delete_statement(self,table:str, where:list[str]=[]) -> str:
        return f"DELETE FROM {table} {" WHERE" + " AND ".join([" " + i + "=?" for i in where])}"
    
    def create_read_statement(self,table:str, values:list[str], where:list[str]=[]) -> str:
        return f"SELECT {",".join(values)} FROM {table}{" WHERE" + " AND ".join([" " + i + " = (?)" for i in where]) if len(where) > 0 else ""}"

    def connect(self) -> None:
        # TODO: would like this if it didn't create a new file if not existing already
        if self.database is None:
            self.database = sqlite3.connect(self.database_path)
            self.cursor = self.database.cursor()

class MySQLDatabase(BaseDatabase):
    def __init__(self, ident: str, database_path: str, connect: bool = True, verbose: bool = True) -> None:
        super().__init__(ident=ident, database_path=database_path, connect=connect, verbose=verbose)
        self.type = "MySQL"
        return

    def create_write_statement(self,table:str,values:list[str]) -> str:
        return f"INSERT INTO {table} ({",".join(values)}) VALUES ({",".join(["%s" for i in range(len(values))])})"
    
    def create_update_statement(self,table:str,values:list[str], where:list[str]=[]) -> str:
        return f"UPDATE {table} SET{",".join([" " + i + "=%s" for i in values])}{" WHERE" + " AND ".join([" " + i + "=%s" for i in where])}"
    
    def create_delete_statement(self,table:str, where:list[str]=[]) -> str:
        return f"DELETE FROM {table} {" WHERE" + " AND ".join([" " + i + "=%s" for i in where])}"

    def create_read_statement(self,table:str, values:list[str], where:list[str]=[]) -> str:
        return f"SELECT {",".join(values)} FROM {table}{" WHERE" + " AND ".join([" " + i + " = (%s)" for i in where]) if len(where) > 0 else ""}"

    def connect(self) -> None:
        if self.database is None:
            self.database = pymysql.connect(host=Bot.DeweyConfig["mysql-host"],
                user=Bot.DeweyConfig["mysql-username"],
                password=Bot.DeweyConfig['mysql-password'],
                database=self.database_path)
            self.cursor = self.database.cursor(cursor=pymysql.cursors.Cursor)
    

def get_db(name:str) -> BaseDatabase | None:
    if name in OpenDatabases.keys():
        return OpenDatabases[name]
    else:
        return None

def setup_db(name:str) -> BaseDatabase:
    newdb = get_db(name=name)
    
    if not newdb:
        if Bot.DeweyConfig["database-type"] == "SQLite3": 
            newdb = SQLite3Database(ident=name, database_path=Bot.DeweyConfig[f"{name}-sqlite-path"], connect=True, verbose=True)
        elif Bot.DeweyConfig["database-type"] == "MySQL":
            newdb = MySQLDatabase(ident=name, database_path=Bot.DeweyConfig[f"mysql-database"], connect=True, verbose=True)
        else: raise Exception("database-type is not SQLite3 or MySQL")
        OpenDatabases[name] = newdb

    return newdb
