"""
models.py
=========
SQLite database layer for storing scan results.
Uses Python's built-in sqlite3 — no ORM needed.
"""

import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'results', 'omr_results.db')


def _get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist."""
    conn = _get_conn()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS scan_results (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp   TEXT NOT NULL,
            image_path  TEXT,
            answer_key  TEXT,   -- JSON
            result      TEXT,   -- JSON (full result dict)
            score       REAL,
            total       INTEGER,
            percentage  REAL,
            student_name TEXT DEFAULT ''
        )
    ''')
    conn.commit()
    conn.close()


def save_result(image_path: str, answer_key: dict, result: dict,
                student_name: str = '') -> int:
    """Insert a scan result row and return the new row id."""
    conn = _get_conn()
    cur  = conn.execute(
        '''INSERT INTO scan_results
           (timestamp, image_path, answer_key, result, score, total, percentage, student_name)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        (
            datetime.utcnow().isoformat(),
            image_path,
            json.dumps(answer_key),
            json.dumps(result),
            result.get('score', 0),
            result.get('total', 0),
            result.get('percentage', 0),
            student_name,
        )
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def get_all_results():
    """Return all scan results as a list of dicts (without heavy JSON blobs)."""
    conn = _get_conn()
    rows = conn.execute(
        'SELECT id, timestamp, score, total, percentage, student_name FROM scan_results ORDER BY id DESC'
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_result_by_id(result_id: int):
    """Return a single result row (full JSON) or None."""
    conn  = _get_conn()
    row   = conn.execute(
        'SELECT * FROM scan_results WHERE id = ?', (result_id,)
    ).fetchone()
    conn.close()
    if row is None:
        return None
    d = dict(row)
    d['answer_key'] = json.loads(d['answer_key'])
    d['result']     = json.loads(d['result'])
    return d


def delete_result(result_id: int):
    """Delete a result by id."""
    conn = _get_conn()
    conn.execute('DELETE FROM scan_results WHERE id = ?', (result_id,))
    conn.commit()
    conn.close()
