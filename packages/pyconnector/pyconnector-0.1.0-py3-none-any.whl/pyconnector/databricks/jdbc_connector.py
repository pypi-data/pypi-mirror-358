try:
    import jaydebeapi
except ImportError:
    jaydebeapi = None

class DatabricksJDBCConnector:
    def __init__(self, token, workspace_url, http_path, version=None):
        jar_path = get_driver("databricks", "jdbc", version)
        self.conn = jaydebeapi.connect(
            "com.databricks.client.jdbc.Driver",
            f"jdbc:databricks://{workspace_url}/;transportMode=http;ssl=1;AuthMech=3;httpPath={http_path};UID=token;PWD={token}",
            ["token", token],
            jar_path
        )

    def cursor(self):
        return self.conn.cursor()

    def close(self):
        self.conn.close()