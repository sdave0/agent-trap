import sqlite3
import os
from contextlib import contextmanager

from agenttrap.db.schema import SCHEMA_SQL

class DBClient:
    def __init__(self, db_path: str = "agenttrap.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initializes the database with the core schema."""
        with self.get_connection() as conn:
            conn.executescript(SCHEMA_SQL)
            conn.commit()

    @contextmanager
    def get_connection(self):
        """Yields a database connection that closes automatically."""
        conn = sqlite3.connect(self.db_path)
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        # Enable WAL mode for better concurrency
        conn.execute("PRAGMA journal_mode = WAL")
        # Return dict-like rows
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
