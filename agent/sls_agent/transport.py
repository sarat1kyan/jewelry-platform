import httpx

class WSClient:
    def __init__(self, cfg):
        self.base = cfg.server_base
        self.token = cfg.token
        self.sess = httpx.Client(timeout=10.0)
    def post(self, path, json_body):
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        try:
            r = self.sess.post(self.base + path, json=json_body, headers=headers)
            return r.json()
        except Exception:
            return {}
    def recv(self):
        return {}
