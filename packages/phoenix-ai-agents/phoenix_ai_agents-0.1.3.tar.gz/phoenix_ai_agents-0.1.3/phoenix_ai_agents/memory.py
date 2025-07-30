
from __future__ import annotations

import json
import logging
import sqlite3
from typing import Any

log = logging.getLogger("phoenix.memory")

class MemoryInterface:
    def save(self, namespace: str, key: str, value: Any): ...
    def load(self, namespace: str, key: str) -> Any: ...
    def query(self, namespace: str, query: str): ...

class SqliteMemory(MemoryInterface):
    def __init__(self, db_path: str = "memory.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("CREATE TABLE IF NOT EXISTS mem (ns TEXT, k TEXT, v TEXT)")
        self.conn.commit()

    def save(self, namespace: str, key: str, value: Any):
        self.conn.execute("INSERT INTO mem (ns,k,v) VALUES (?,?,?)", (namespace, key, json.dumps(value)))
        self.conn.commit()

    def load(self, namespace: str, key: str):
        cur = self.conn.execute("SELECT v FROM mem WHERE ns=? AND k=?", (namespace, key))
        row = cur.fetchone()
        return json.loads(row[0]) if row else None
