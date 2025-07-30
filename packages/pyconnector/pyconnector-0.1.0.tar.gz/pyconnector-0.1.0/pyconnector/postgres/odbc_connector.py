from pyconnector.driver_utils import get_driver
import pyodbc

class PostgresODBCConnector:
    def __init__(self, host, port, database, user, password, version=None):
        driver_path = get_driver("postgres", "odbc", version)
        conn_str = (
            f"Driver={{{driver_path}}};Server={host};Port={port};Database={database};"
            f"UID={user};PWD={password};"
        )
        self.conn = pyodbc.connect(conn_str, autocommit=True)

    def cursor(self):
        return self.conn.cursor()

    def close(self):
        self.conn.close()