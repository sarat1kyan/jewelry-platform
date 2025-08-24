import time, platform, getpass, socket, httpx

BASE_URL = "https://kaktusing.org"   # make sure this matches your domain
AGENT_ID = socket.gethostname()
USER     = getpass.getuser()

def register():
    payload = {
        "agent_id": AGENT_ID,
        "user": USER,
        "hostname": AGENT_ID,
    }
    r = httpx.post(f"{BASE_URL}/api/agents/register", json=payload, timeout=10)
    print("REGISTER:", r.status_code, r.text)

def heartbeat():
    payload = {
        "agent_id": AGENT_ID,
        "os_version": platform.platform(),
        "rhino_version": "8",
        "is_rhino_running": False,
        "is_rhino_foreground": False,
        "active_task_id": None,
        "cpu_5m": 1.0,
        "idle_minutes": 2,
    }
    r = httpx.post(f"{BASE_URL}/api/agents/heartbeat", json=payload, timeout=10)
    print("HEARTBEAT:", r.status_code, r.text)

if __name__ == "__main__":
    register()
    while True:
        heartbeat()
        time.sleep(30)
