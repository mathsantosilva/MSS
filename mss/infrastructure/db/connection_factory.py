import pyodbc

class SqlConnectionFactory:
    def __init__(self, encrypt="not"):
        self.encrypt = encrypt

    def connect(self, server, username, password, database=None, autocommit=False):
        base = f"DRIVER=SQL Server;SERVER={server};ENCRYPT={self.encrypt};UID={username};PWD={password}"
        if database:
            base += f";DATABASE={database}"
        return pyodbc.connect(base, autocommit=autocommit)
