"""In-memory job progress for SSE."""
import threading, time, uuid
from typing import Any, Optional
_lock = threading.Lock()
_jobs = {}

def create_job(kind="scan"):
    jid = uuid.uuid4().hex[:12]
    with _lock:
        _jobs[jid] = {"id": jid, "kind": kind, "percent": 0, "stage": "starting", "message": "", "done": False, "error": None, "result": None, "created": time.time()}
    return jid

def update_job(jid, percent=None, stage="", message=""):
    with _lock:
        j = _jobs.get(jid)
        if not j: return
        if percent is not None: j["percent"] = max(0, min(100, int(percent)))
        if stage: j["stage"] = stage
        if message: j["message"] = message

def finish_job(jid, result=None, error=None):
    with _lock:
        j = _jobs.get(jid)
        if not j: return
        j["done"] = True
        j["percent"] = 100 if not error else j.get("percent", 0)
        j["result"] = result
        j["error"] = error
        j["stage"] = "error" if error else "done"

def get_job(jid):
    with _lock:
        j = _jobs.get(jid)
        return dict(j) if j else None
