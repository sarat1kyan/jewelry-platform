# sls_agent/config.py
import os, getpass, socket, httpx

class Config:
    def __init__(self):
        self.base = os.getenv("SLS_BASE", "https://kaktusing.org").rstrip("/")
        self.agent_id = os.getenv("SLS_AGENT_ID", socket.gethostname())
        self.user = getpass.getuser()
        self.hostname = socket.gethostname()
        self.job_root = os.getenv("JOB_ROOT", r"C:\SLS\Jobs")
        self.token = os.getenv("SLS_TOKEN", "")
        self.active_task_id = None

    @staticmethod
    def load():
        # Optionally parse .env here if you want
        return Config()

    def http_post(self, path: str, json: dict):
        url = f"{self.base}{path}"
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        r = httpx.post(url, json=json, headers=headers, timeout=15)
        r.raise_for_status()
        return r.json()
