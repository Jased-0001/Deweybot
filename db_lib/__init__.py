import sqlite3

OpenDatabases = {}

class Database:
    def __init__(self,ident: str, database_path: str, tables: list[str] | None = None, connect: bool = True, verbose: bool = True) -> None:
        self.ident: str = ident
        self.database_path: str = database_path
        self.tables: list[str] | None = tables

        self.database: sqlite3.Connection | None = None
        self.cursor: sqlite3.Cursor | None = None

        self.verbose: bool = verbose

        if connect: 
            self.connect()
        if tables:
            self.setup_tables(tables=tables)

        print(f" [SQL] [{self.ident}] opened db '{self.database_path}' ({"connected" if connect else "not connected"})")
    
    def connect(self) -> None:
        if self.database is None:
            self.database = sqlite3.connect(self.database_path)
            self.cursor = self.database.cursor()

    def setup_tables(self, tables:list[str]) -> None:
        if self.database and self.cursor:
            for i in tables:
                try:
                    self.cursor.execute(i)
                except sqlite3.OperationalError as e:
                    msg = str(e)
                    if msg.startswith("table ") and msg.endswith(" already exists"):
                        print(f" [SQL] [{self.ident}] {msg}")
                    else:
                        raise e
            
            self.database.commit()
        else:
            raise Exception("database was not connected")
    
    def write_data(self, statement: str, data: tuple) -> None:
        if self.database and self.cursor:
            if self.verbose: print(f" [SQL] [{self.ident}] write '{statement}' , '{data}")
            self.cursor.execute(statement, data)
            self.database.commit()
        else:
            raise Exception("database was not connected")
    
    def read_data(self, statement: str, parameters: tuple = ()) -> list:
        if self.database and self.cursor:
            if self.verbose: print(f" [SQL] [{self.ident}] read '{statement}' , '{parameters}")
            return self.cursor.execute(statement, parameters).fetchall()
        else:
            raise Exception("database was not connected")
    
    def close_connection(self):
        if self.database is not None:
            self.database.close()

    def __repr__(self) -> str:
        return f"(DB '{self.ident}'@'{self.database_path}' ({'connected' if self.database else 'not connected'}{', verbose' if self.verbose else ''}))"
    

def get_db(name:str) -> Database | None:
    if name in OpenDatabases.keys():
        return OpenDatabases[name]
    else:
        return None

def setup_db(name:str, tables:list[str], file:str) -> Database:
    newdb = get_db(name=name)
    
    if not newdb:
        newdb = Database(ident=name, database_path=file, tables=tables, connect=True)
        OpenDatabases[name] = newdb

    return newdb
