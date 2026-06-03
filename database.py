import sqlite3
from datetime import datetime

DB_NAME = "interview_history.db"

def init_db():
    """Creates the analytical tracking storage matrix if not initialized."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            role TEXT,
            accuracy REAL,
            communication REAL,
            problem_solving REAL,
            pacing REAL,
            feedback TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_session(role, accuracy, communication, problem_solving, pacing, feedback):
    """Logs numerical telemetry and written feedback profiles securely."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute('''
        INSERT INTO sessions (date, role, accuracy, communication, problem_solving, pacing, feedback)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (date_str, role, accuracy, communication, problem_solving, pacing, feedback))
    conn.commit()
    conn.close()

def get_all_sessions():
    """Retrieves chronological database metrics for historical data plotting."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT date, role, accuracy, communication, problem_solving, pacing, feedback 
        FROM sessions ORDER BY id ASC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return rows