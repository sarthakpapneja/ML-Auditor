"""
ModelAuditAI — Backend Database Layer
SQLite metadata storage for audit runs.
"""
import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "metadata.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS audits (
            id TEXT PRIMARY KEY,
            status TEXT NOT NULL DEFAULT 'pending',
            model_filename TEXT,
            dataset_filename TEXT,
            target_column TEXT,
            task_type TEXT,
            created_at TEXT NOT NULL,
            completed_at TEXT,
            results_path TEXT,
            health_score REAL,
            error TEXT
        )
    """)
    conn.commit()
    conn.close()


def create_audit(audit_id: str, model_filename: str, dataset_filename: str,
                 target_column: str, task_type: str) -> dict:
    conn = get_connection()
    now = datetime.utcnow().isoformat()
    conn.execute(
        "INSERT INTO audits (id, status, model_filename, dataset_filename, target_column, task_type, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (audit_id, "pending", model_filename, dataset_filename, target_column, task_type, now)
    )
    conn.commit()
    row = conn.execute("SELECT * FROM audits WHERE id = ?", (audit_id,)).fetchone()
    conn.close()
    return dict(row)


def update_audit(audit_id: str, **kwargs):
    conn = get_connection()
    sets = ", ".join(f"{k} = ?" for k in kwargs)
    vals = list(kwargs.values()) + [audit_id]
    conn.execute(f"UPDATE audits SET {sets} WHERE id = ?", vals)
    conn.commit()
    conn.close()


def get_audit(audit_id: str) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM audits WHERE id = ?", (audit_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def list_audits() -> list[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM audits ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


init_db()
