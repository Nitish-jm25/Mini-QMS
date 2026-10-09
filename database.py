# database.py

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent / "qms.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with get_connection() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            team_name TEXT NOT NULL,
            start_date TEXT NOT NULL,
            deadline TEXT NOT NULL,
            description TEXT DEFAULT '',
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS risks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            category TEXT NOT NULL,
            probability INTEGER NOT NULL CHECK(probability BETWEEN 1 AND 5),
            impact INTEGER NOT NULL CHECK(impact BETWEEN 1 AND 5),
            score INTEGER NOT NULL CHECK(score BETWEEN 1 AND 25),
            level TEXT NOT NULL,
            owner TEXT NOT NULL,
            mitigation TEXT DEFAULT '',
            status TEXT NOT NULL DEFAULT 'Open',
            due_date TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY(project_id) REFERENCES projects(id)
                ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS risk_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            risk_id INTEGER NOT NULL,
            old_status TEXT,
            new_status TEXT NOT NULL,
            remarks TEXT DEFAULT '',
            changed_at TEXT NOT NULL,
            FOREIGN KEY(risk_id) REFERENCES risks(id)
                ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_risks_project
        ON risks(project_id);

        CREATE INDEX IF NOT EXISTS idx_risks_status
        ON risks(status);
        """)


def create_project(name, team_name, start_date, deadline, description):
    now = datetime.now().isoformat(timespec="seconds")

    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO projects
            (name, team_name, start_date, deadline, description, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            name.strip(), team_name.strip(), str(start_date),
            str(deadline), description.strip(), now
        ))
        return cursor.lastrowid


def get_projects():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT p.*,
                (SELECT COUNT(*) FROM risks r
                 WHERE r.project_id = p.id) AS total_risks
            FROM projects p
            ORDER BY p.id DESC
        """).fetchall()
        return [dict(row) for row in rows]


def delete_project(project_id):
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM projects WHERE id = ?", (project_id,)
        )


def create_risk(data):
    now = datetime.now().isoformat(timespec="seconds")

    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO risks (
                project_id, title, description, category,
                probability, impact, score, level, owner,
                mitigation, status, due_date, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["project_id"], data["title"].strip(),
            data["description"].strip(), data["category"],
            data["probability"], data["impact"], data["score"],
            data["level"], data["owner"].strip(),
            data["mitigation"].strip(), data["status"],
            data["due_date"], now, now
        ))

        risk_id = cursor.lastrowid

        conn.execute("""
            INSERT INTO risk_history
            (risk_id, old_status, new_status, remarks, changed_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            risk_id, None, data["status"],
            "Risk registered", now
        ))

        return risk_id


def get_risks(project_id=None):
    query = """
        SELECT r.*, p.name AS project_name
        FROM risks r
        JOIN projects p ON p.id = r.project_id
    """
    params = ()

    if project_id is not None:
        query += " WHERE r.project_id = ?"
        params = (project_id,)

    query += " ORDER BY r.score DESC, r.id DESC"

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]


def update_risk(risk_id, data):
    now = datetime.now().isoformat(timespec="seconds")

    with get_connection() as conn:
        row = conn.execute(
            "SELECT status FROM risks WHERE id = ?", (risk_id,)
        ).fetchone()

        if row is None:
            raise ValueError("Risk not found.")

        old_status = row["status"]

        conn.execute("""
            UPDATE risks SET
                title = ?, description = ?, category = ?,
                probability = ?, impact = ?, score = ?, level = ?,
                owner = ?, mitigation = ?, status = ?,
                due_date = ?, updated_at = ?
            WHERE id = ?
        """, (
            data["title"].strip(), data["description"].strip(),
            data["category"], data["probability"], data["impact"],
            data["score"], data["level"], data["owner"].strip(),
            data["mitigation"].strip(), data["status"],
            data["due_date"], now, risk_id
        ))

        if old_status != data["status"]:
            conn.execute("""
                INSERT INTO risk_history
                (risk_id, old_status, new_status, remarks, changed_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                risk_id, old_status, data["status"],
                "Status updated through QMS", now
            ))


def delete_risk(risk_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM risks WHERE id = ?", (risk_id,))


def get_history(project_id=None):
    query = """
        SELECT h.*, r.title AS risk_title, p.name AS project_name
        FROM risk_history h
        JOIN risks r ON r.id = h.risk_id
        JOIN projects p ON p.id = r.project_id
    """
    params = ()

    if project_id is not None:
        query += " WHERE p.id = ?"
        params = (project_id,)

    query += " ORDER BY h.id DESC"

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]