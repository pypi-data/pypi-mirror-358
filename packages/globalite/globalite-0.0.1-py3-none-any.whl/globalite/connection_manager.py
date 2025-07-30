from __future__ import annotations
from typing import Optional
import sqlite3


class _ConnectionManager:

    def __init__(self, db_file_path: str):
        self._db_file_path: str = db_file_path
        self._conn: Optional[sqlite3.Connection] = None

    def __enter__(self) -> tuple[sqlite3.Connection, sqlite3.Cursor]:
        self._conn = sqlite3.connect(self._db_file_path)
        return self._conn, self._conn.cursor()

    def __exit__(self, *_):
        self._conn.close()
