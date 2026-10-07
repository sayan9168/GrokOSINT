"""Case Manager — SQLite investigation workspace."""
import json, sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

DEFAULT_DB = "reports/grokosint_cases.db"

class CaseManager:
    def __init__(self, db_path: str = DEFAULT_DB):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _conn(self):
        c = sqlite3.connect(self.db_path)
        c.row_factory = sqlite3.Row
        return c

    def _init(self):
        with self._conn() as con:
            con.executescript('''
                CREATE TABLE IF NOT EXISTS cases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL, description TEXT DEFAULT '',
                    tags TEXT DEFAULT '[]', created_at TEXT, updated_at TEXT);
                CREATE TABLE IF NOT EXISTS case_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, case_id INTEGER NOT NULL,
                    seed TEXT NOT NULL, seed_type TEXT DEFAULT '', label TEXT DEFAULT '',
                    data_json TEXT DEFAULT '{}', notes TEXT DEFAULT '', created_at TEXT);
                CREATE TABLE IF NOT EXISTS case_notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, case_id INTEGER NOT NULL,
                    body TEXT NOT NULL, created_at TEXT);
            ''')

    def _now(self):
        return datetime.now(timezone.utc).isoformat()

    def create_case(self, title, description="", tags=None):
        now = self._now()
        with self._conn() as con:
            cur = con.execute(
                "INSERT INTO cases (title, description, tags, created_at, updated_at) VALUES (?,?,?,?,?)",
                (title, description, json.dumps(tags or []), now, now))
            return int(cur.lastrowid)

    def list_cases(self):
        with self._conn() as con:
            rows = con.execute("SELECT * FROM cases ORDER BY updated_at DESC").fetchall()
        out = []
        for r in rows:
            d = dict(r); d["tags"] = json.loads(d.get("tags") or "[]")
            with self._conn() as con:
                d["item_count"] = con.execute("SELECT COUNT(*) FROM case_items WHERE case_id=?", (d["id"],)).fetchone()[0]
            out.append(d)
        return out

    def get_case(self, case_id):
        with self._conn() as con:
            row = con.execute("SELECT * FROM cases WHERE id=?", (case_id,)).fetchone()
            if not row: return None
            d = dict(row); d["tags"] = json.loads(d.get("tags") or "[]")
            d["items"] = [dict(i) for i in con.execute(
                "SELECT id, seed, seed_type, label, notes, created_at FROM case_items WHERE case_id=? ORDER BY id", (case_id,)).fetchall()]
            d["notes"] = [dict(n) for n in con.execute(
                "SELECT id, body, created_at FROM case_notes WHERE case_id=? ORDER BY id DESC", (case_id,)).fetchall()]
        return d

    def add_item(self, case_id, seed, seed_type="", label="", data=None, notes=""):
        now = self._now()
        with self._conn() as con:
            cur = con.execute(
                "INSERT INTO case_items (case_id, seed, seed_type, label, data_json, notes, created_at) VALUES (?,?,?,?,?,?,?)",
                (case_id, seed, seed_type, label or seed, json.dumps(data or {}, default=str), notes, now))
            con.execute("UPDATE cases SET updated_at=? WHERE id=?", (now, case_id))
            return int(cur.lastrowid)

    def add_note(self, case_id, body):
        now = self._now()
        with self._conn() as con:
            cur = con.execute("INSERT INTO case_notes (case_id, body, created_at) VALUES (?,?,?)", (case_id, body, now))
            con.execute("UPDATE cases SET updated_at=? WHERE id=?", (now, case_id))
            return int(cur.lastrowid)

    def delete_case(self, case_id):
        with self._conn() as con:
            con.execute("DELETE FROM case_notes WHERE case_id=?", (case_id,))
            con.execute("DELETE FROM case_items WHERE case_id=?", (case_id,))
            return con.execute("DELETE FROM cases WHERE id=?", (case_id,)).rowcount > 0
