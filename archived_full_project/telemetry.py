# # ghosteye/telemetry.py
# from __future__ import annotations
# from dataclasses import dataclass
# from datetime import datetime
# from typing import Any, Callable, Dict, List
# import json, uuid

# class EventBus:
#     def __init__(self):
#         self._subs: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}
#     def on(self, event: str, fn: Callable[[Dict[str, Any]], None]):
#         self._subs.setdefault(event, []).append(fn)
#     def emit(self, event: str, **payload: Any):
#         for fn in self._subs.get(event, []):
#             fn({"event": event, **payload})

# @dataclass
# class Telemetry:
#     bus: EventBus
#     def __post_init__(self):
#         for e in ["SCHEDULED", "DISPATCHED", "DELIVERED", "INBOUND"]:
#             self.bus.on(e, self._log)
#     def _log(self, ev: Dict[str, Any]):
#         ev = {"ts": datetime.utcnow().isoformat()+"Z", "trace_id": ev.get("trace_id") or uuid.uuid4().hex, **ev}
#         print(json.dumps(ev))


# ghosteye/telemetry.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
import json, uuid
from .logger import NDJSONLogger

class EventBus:
    def __init__(self):
        self._subs: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}
    def on(self, event: str, fn: Callable[[Dict[str, Any]], None]):
        self._subs.setdefault(event, []).append(fn)
    def emit(self, event: str, **payload: Any):
        for fn in self._subs.get(event, []):
            fn({"event": event, **payload})

@dataclass
class Telemetry:
    bus: EventBus
    logfile: str = "logs.ndjson"
    _logger: Optional[NDJSONLogger] = None

    def __post_init__(self):
        self._logger = NDJSONLogger(self.logfile)
        for e in ["SCHEDULED", "DISPATCHED", "DELIVERED", "INBOUND"]:
            self.bus.on(e, self._log)

    def _log(self, ev: Dict[str, Any]):
        ev = {"ts": datetime.utcnow().isoformat()+"Z", "trace_id": ev.get("trace_id") or uuid.uuid4().hex, **ev}
        print(json.dumps(ev))          # console
        self._logger.write(ev)         # durable NDJSON
