# ghosteye/logger.py
from __future__ import annotations
import json, threading
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

class NDJSONLogger:
    def __init__(self, path: str = "logs.ndjson"):
        self.path = path
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def write(self, ev: Dict[str, Any]):
        ev = {"ts": ev.get("ts") or datetime.utcnow().isoformat() + "Z", **ev}
        line = json.dumps(ev, ensure_ascii=False)
        with self._lock:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(line + "\n")
