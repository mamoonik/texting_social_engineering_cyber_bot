# ghosteye/storage.py
from __future__ import annotations
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

class HistoryStore:
    def __init__(self, path: str = "ghosteye.db"):
        self.path = path
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.path, check_same_thread=False, detect_types=sqlite3.PARSE_DECLTYPES)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS sends (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              from_number TEXT NOT NULL,
              sent_at TIMESTAMP NOT NULL
            )
        """)
        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_sends_from_ts ON sends(from_number, sent_at)
        """)
        self._conn.commit()

    def get_history(self, from_number: str, lookback_hours: int = 24) -> List[datetime]:
        cur = self._conn.cursor()
        since = datetime.utcnow() - timedelta(hours=lookback_hours)
        cur.execute(
            "SELECT sent_at FROM sends WHERE from_number=? AND sent_at>=? ORDER BY sent_at ASC",
            (from_number, since)
        )
        return [row[0] if isinstance(row[0], datetime) else datetime.fromisoformat(row[0]) for row in cur.fetchall()]

    def record_send(self, from_number: str, when_utc: datetime) -> None:
        self._conn.execute(
            "INSERT INTO sends(from_number, sent_at) VALUES (?, ?)",
            (from_number, when_utc.isoformat())
        )
        self._conn.commit()
