# sls_agent/agent.py
import time, threading
from .config import Config
from .rhino_watch import RhinoWatcher
from .fs_watch import DoneFileWatcher
from .gui import toast

INACTIVITY_MINUTES = 15

def run():
    cfg = Config.load()
    rhino = RhinoWatcher()
    fsw = DoneFileWatcher(cfg)

    # Register
    cfg.http_post("/api/agents/register", {
        "agent_id": cfg.agent_id,
        "user": cfg.user,
        "hostname": cfg.hostname,
    })

    last_active_ts = time.time()
    inactive_alerted = False

    def hb_loop():
        nonlocal last_active_ts, inactive_alerted
        while True:
            snap = rhino.snapshot()
            if snap["is_rhino_running"] or snap["is_rhino_foreground"]:
                last_active_ts = time.time()
                inactive_alerted = False
            hb = {
                "agent_id": cfg.agent_id,
                "os_version": "",  # optional; fill if you want
                "rhino_version": snap["rhino_version"],
                "is_rhino_running": snap["is_rhino_running"],
                "is_rhino_foreground": snap["is_rhino_foreground"],
                "active_task_id": cfg.active_task_id,
                "cpu_5m": 0.0,  # keep simple, or compute rolling avg
                "idle_minutes": snap["idle_minutes"],
            }
            try:
                cfg.http_post("/api/agents/heartbeat", hb)
            except Exception:
                pass

            # inactivity detection
            mins_since_active = (time.time() - last_active_ts) / 60.0
            if cfg.active_task_id and mins_since_active >= INACTIVITY_MINUTES and not inactive_alerted:
                try:
                    toast("You have an active SLS task. Please resume Rhino.")
                except Exception:
                    pass
                try:
                    cfg.http_post("/api/agents/event", {
                        "agent_id": cfg.agent_id,
                        "type": "inactive_15m",
                        "task_id": cfg.active_task_id
                    })
                except Exception:
                    pass
                inactive_alerted = True

            time.sleep(30)

    threading.Thread(target=hb_loop, daemon=True).start()

    # In a simple build we don’t run a WS loop yet; we only react to assignment
    # via Telegram → server → push to agent (HTTP long-poll can be added later).

    while True:
        time.sleep(3600)  # keep process alive

if __name__ == "__main__":
    run()
