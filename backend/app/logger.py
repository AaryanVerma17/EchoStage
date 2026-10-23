import json
from pathlib import Path
from threading import Lock
from .config import get_settings

_lock = Lock()

def _path():
    p = Path(get_settings().event_log_path)
    return p if p.is_absolute() else Path(__file__).resolve().parents[1] / p

def append_event(event):
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with _lock, path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

def read_events(limit=50):
    path = _path()
    if not path.exists():
        return []
    with _lock:
        lines = path.read_text(encoding="utf-8").splitlines()
    output = []
    for line in lines[-max(1, min(limit, 500)):]:
        try:
            output.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return list(reversed(output))
