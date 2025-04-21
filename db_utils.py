# db_utils.py
import sqlite3
import time
from datetime import datetime, timedelta

def init_db():
    conn = sqlite3.connect("rps_history.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS moves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            choice TEXT,
            ai_choice TEXT,
            result TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def _clean_old_records():
    """Delete records older than 1 hour"""
    conn = sqlite3.connect("rps_history.db")
    c = conn.cursor()
    
    # Calculate timestamp from 1 hour ago
    one_hour_ago = datetime.now() - timedelta(hours=1)
    timestamp_str = one_hour_ago.strftime('%Y-%m-%d %H:%M:%S')
    
    c.execute("DELETE FROM moves WHERE timestamp < ?", (timestamp_str,))
    conn.commit()
    conn.close()

def add_move(username, choice, ai_choice, result):
    conn = sqlite3.connect("rps_history.db")
    c = conn.cursor()
    
    # First clean old records
    _clean_old_records()
    
    # Then add new move
    c.execute(
        "INSERT INTO moves (username, choice, ai_choice, result) VALUES (?, ?, ?, ?)",
        (username, choice, ai_choice, result)
    )
    conn.commit()
    conn.close()

def get_user_history(username):
    conn = sqlite3.connect("rps_history.db")
    c = conn.cursor()
    
    # First clean old records
    _clean_old_records()
    
    # Then fetch remaining history
    c.execute("""
        SELECT choice, ai_choice, result 
        FROM moves 
        WHERE username = ? 
        ORDER BY timestamp DESC
    """, (username,))
    rows = c.fetchall()
    conn.close()
    return rows