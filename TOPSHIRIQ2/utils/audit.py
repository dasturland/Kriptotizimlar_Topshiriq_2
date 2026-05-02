import sqlite3
from datetime import datetime


def log_event(db_path, username, event):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('INSERT INTO audit (username, event) VALUES (?, ?)', (username, event))
    conn.commit()
    conn.close()
