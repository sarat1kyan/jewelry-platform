# sls_agent/rhino_watch.py
import psutil, time, ctypes, win32gui, win32process

RHINO_EXE_NAMES = {"rhino.exe", "rhino5.exe", "rhino6.exe", "rhino7.exe", "rhino8.exe"}

def _get_foreground_pid():
    try:
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd:
            return None
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        return pid
    except Exception:
        return None

def _os_idle_minutes():
    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]
    lastInputInfo = LASTINPUTINFO()
    lastInputInfo.cbSize = ctypes.sizeof(LASTINPUTINFO)
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lastInputInfo))
    millis = ctypes.windll.kernel32.GetTickCount() - lastInputInfo.dwTime
    return int(millis / 1000 / 60)

class RhinoWatcher:
    """
    Snapshot-only helper, stateless. The agent loop decides what to alert/report.
    """
    def snapshot(self):
        procs = []
        foreground_pid = _get_foreground_pid()
        rhino_running = False
        rhino_foreground = False
        rhino_version = None

        for p in psutil.process_iter(attrs=["pid","name","cpu_percent"]):
            n = (p.info.get("name") or "").lower()
            if n in RHINO_EXE_NAMES:
                rhino_running = True
                if p.info["pid"] == foreground_pid:
                    rhino_foreground = True
                # naive version inference from name
                if "8" in n: rhino_version = "8"
                elif "7" in n: rhino_version = "7"
                elif "6" in n: rhino_version = "6"
                elif "5" in n: rhino_version = "5"
                else: rhino_version = rhino_version or "unknown"
                procs.append(p.info)

        return {
            "is_rhino_running": rhino_running,
            "is_rhino_foreground": rhino_foreground,
            "rhino_version": rhino_version or "unknown",
            "idle_minutes": _os_idle_minutes(),
        }
