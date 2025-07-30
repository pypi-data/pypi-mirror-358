from pyconnector.driver_utils import get_driver
import pyodbc

class DatabricksODBCConnector:
    def __init__(self, token, workspace_url, http_path, version=None):
        driver_path = get_driver("databricks", "odbc", version)
        conn_str = (
            f"Driver={{{driver_path}}};Host={workspace_url};HTTPPath={http_path};"
            f"AuthMech=3;UID=token;PWD={token};"
        )
        self.conn = pyodbc.connect(conn_str, autocommit=True)

    def cursor(self):
        return self.conn.cursor()

    def close(self):
        self.conn.close()