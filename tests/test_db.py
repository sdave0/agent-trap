import pytest
import sqlite3
import os
from agenttrap.db.client import DBClient

def test_db_initialization(tmp_path):
    db_path = tmp_path / "test.db"
    client = DBClient(db_path=str(db_path))
    
    with client.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = {row['name'] for row in cursor.fetchall()}
        
        expected_tables = {'runs', 'scenario_results', 'action_traces'}
        assert expected_tables.issubset(tables)
