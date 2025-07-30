import requests

class PostgresAPIConnector:
    def __init__(self, base_url, token):
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        self.base_url = base_url.rstrip("/")

    def get(self, endpoint, params=None):
        res = self.session.get(f"{self.base_url}{endpoint}", params=params)
        res.raise_for_status()
        return res.json()

    def post(self, endpoint, data=None):
        res = self.session.post(f"{self.base_url}{endpoint}", json=data)
        res.raise_for_status()
        return res.json()
