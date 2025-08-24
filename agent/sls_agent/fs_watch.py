# sls_agent/fs_watch.py
import os, time, threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class _DoneHandler(FileSystemEventHandler):
    def __init__(self, on_done):
        self.on_done = on_done
    def on_created(self, event):
        if event.is_directory: return
        if event.src_path.lower().endswith("_done.3dm"):
            self.on_done(event.src_path)

class DoneFileWatcher:
    def __init__(self, cfg):
        self.cfg = cfg
        self.observer = None
        self.watch_path = None

    def ensure_folder(self, path):
        self.watch_path = path or self.cfg.job_root
        os.makedirs(self.watch_path, exist_ok=True)
        if self.observer:  # re-arm
            self.observer.stop(); self.observer.join()
        self.observer = Observer()
        self.observer.schedule(_DoneHandler(self._on_done), self.watch_path, recursive=False)
        self.observer.start()

    def _on_done(self, filepath):
        # Notify server immediately
        self.cfg.http_post("/api/agents/event", {
            "agent_id": self.cfg.agent_id,
            "type": "file_done",
            "path": filepath
        })

    def stop(self):
        if self.observer:
            self.observer.stop(); self.observer.join()
            self.observer = None
