from pyconnector.driver_utils import get_driver
import jaydebeapi

class PostgresJDBCConnector:
    def __init__(self, host, port, database, user, password, version=None):
        jar_path = get_driver("postgres", "jdbc", version)
        self.conn = jaydebeapi.connect(
            "org.postgresql.Driver",
            f"jdbc:postgresql://{host}:{port}/{database}",
            [user, password],
            jar_path
        )

    def cursor(self):
        return self.conn.cursor()

    def close(self):
        self.conn.close()