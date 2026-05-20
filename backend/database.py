import sqlite3
from pathlib import Path
from datetime import datetime

#DB_PATH = Path(__file__).parent / "mindsphere.db"
from backend.config import DB_PATH


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Chat history
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # Journal entries
    cur.execute("""
        CREATE TABLE IF NOT EXISTS journal_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            sentiment TEXT,
            themes TEXT,
            ai_reflection TEXT,
            created_at TEXT NOT NULL
        )
    """)

    # Mood logs
    cur.execute("""
        CREATE TABLE IF NOT EXISTS mood_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mood_score INTEGER NOT NULL,
            note TEXT,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    print(f"DB ready at {DB_PATH}")


# Chat helpers
def save_message(role: str, content: str):
    conn = get_connection()
    conn.execute(
        "INSERT INTO chat_messages (role, content, created_at) VALUES (?, ?, ?)",
        (role, content, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def get_chat_history(limit: int = 50):
    conn = get_connection()
    rows = conn.execute(
        "SELECT role, content, created_at FROM chat_messages ORDER BY id ASC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def clear_chat_history():
    conn = get_connection()
    conn.execute("DELETE FROM chat_messages")
    conn.commit()
    conn.close()


# Journal helpers
def save_journal(content: str, sentiment: str, themes: str, ai_reflection: str):
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO journal_entries
           (content, sentiment, themes, ai_reflection, created_at)
           VALUES (?, ?, ?, ?, ?)""",
        (content, sentiment, themes, ai_reflection, datetime.utcnow().isoformat()),
    )
    entry_id = cur.lastrowid
    conn.commit()
    conn.close()
    return entry_id


def get_journal_entries(limit: int = 100):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM journal_entries ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# Mood helpers
def save_mood(mood_score: int, note: str = ""):
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO mood_logs (mood_score, note, created_at) VALUES (?, ?, ?)",
        (mood_score, note, datetime.utcnow().isoformat()),
    )
    mood_id = cur.lastrowid
    conn.commit()
    conn.close()
    return mood_id


def get_mood_logs(limit: int = 100):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM mood_logs ORDER BY id ASC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


if __name__ == "__main__":
    init_db()