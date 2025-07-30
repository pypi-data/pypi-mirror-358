import requests

class DatabricksAPIConnector:
    def __init__(self, token: str, workspace_url: str):
        if not token or not workspace_url:
            raise ValueError("token and workspace_url required.")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {token.strip()}"
        })
        self.workspace_url = workspace_url.rstrip("/")

    def get(self, endpoint: str, params=None):
        res = self.session.get(f"{self.workspace_url}{endpoint}", params=params)
        res.raise_for_status()
        return res.json()

    def post(self, endpoint: str, data=None):
        res = self.session.post(f"{self.workspace_url}{endpoint}", json=data)
        res.raise_for_status()
        return res.json()
