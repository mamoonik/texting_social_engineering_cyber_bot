# ghosteye/store.py
from __future__ import annotations
import os, sqlite3
from datetime import datetime
from typing import List, Dict, Any, Tuple

DB_PATH = os.getenv("GHOSTEYE_DB", "data/ghosteye.db")

def _conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    cx = sqlite3.connect(DB_PATH)
    cx.row_factory = sqlite3.Row
    return cx

def init_db():
    with _conn() as cx:
        cx.executescript("""
        CREATE TABLE IF NOT EXISTS conversations (
          conv_id TEXT PRIMARY KEY,
          created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS messages (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          conv_id TEXT NOT NULL,
          ts TEXT NOT NULL,
          actor TEXT NOT NULL CHECK(actor IN ('employee','recruiter')),
          text TEXT NOT NULL,
          FOREIGN KEY(conv_id) REFERENCES conversations(conv_id)
        );
        CREATE INDEX IF NOT EXISTS idx_messages_conv_ts ON messages(conv_id, ts);

        CREATE TABLE IF NOT EXISTS summaries (
          conv_id TEXT PRIMARY KEY,
          summary TEXT NOT NULL,
          last_msg_id INTEGER NOT NULL DEFAULT 0
        );
        """)
    return DB_PATH

def ensure_conversation(conv_id: str):
    with _conn() as cx:
        cx.execute(
            "INSERT OR IGNORE INTO conversations(conv_id, created_at) VALUES(?, ?)",
            (conv_id, datetime.utcnow().isoformat() + "Z")
        )

def add_message(conv_id: str, actor: str, text: str) -> int:
    ensure_conversation(conv_id)
    with _conn() as cx:
        cur = cx.execute(
            "INSERT INTO messages(conv_id, ts, actor, text) VALUES(?, ?, ?, ?)",
            (conv_id, datetime.utcnow().isoformat() + "Z", actor, text)
        )
        return int(cur.lastrowid)

def fetch_recent(conv_id: str, limit: int = 16) -> List[Dict[str, Any]]:
    with _conn() as cx:
        cur = cx.execute(
            "SELECT id, conv_id, ts, actor, text FROM messages WHERE conv_id=? ORDER BY id DESC LIMIT ?",
            (conv_id, limit)
        )
        rows = list(reversed(cur.fetchall()))
    return [dict(r) for r in rows]

def get_summary(conv_id: str) -> Tuple[str, int]:
    with _conn() as cx:
        cur = cx.execute("SELECT summary, last_msg_id FROM summaries WHERE conv_id=?", (conv_id,))
        row = cur.fetchone()
    if not row:
        return ("", 0)
    return (row["summary"], int(row["last_msg_id"]))

def save_summary(conv_id: str, summary: str, last_msg_id: int):
    with _conn() as cx:
        cx.execute(
            "INSERT INTO summaries(conv_id, summary, last_msg_id) VALUES(?, ?, ?) "
            "ON CONFLICT(conv_id) DO UPDATE SET summary=excluded.summary, last_msg_id=excluded.last_msg_id",
            (conv_id, summary, last_msg_id)
        )