import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'phishaware.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            department TEXT NOT NULL,
            awareness_score INTEGER DEFAULT 100
        )
    ''')

    # Emails table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            subject TEXT NOT NULL,
            body TEXT NOT NULL,
            is_phishing INTEGER NOT NULL,
            indicators TEXT,
            landing_url TEXT
        )
    ''')

    # Events table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS security_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            username TEXT NOT NULL,
            event_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            details TEXT NOT NULL
        )
    ''')

    # User decisions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            username TEXT NOT NULL,
            email_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            risk_level TEXT NOT NULL,
            FOREIGN KEY (email_id) REFERENCES emails (id)
        )
    ''')

    # Incident state table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incident_state (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_number TEXT NOT NULL DEFAULT 'INCIDENT #001',
            incident_type TEXT NOT NULL DEFAULT 'Simulated Phishing',
            severity TEXT NOT NULL DEFAULT 'Medium',
            status TEXT NOT NULL DEFAULT 'Detected', -- Detected, Contained, Eradicated, Recovered
            campaign_disabled INTEGER DEFAULT 0,
            url_blocked INTEGER DEFAULT 0,
            artifacts_removed INTEGER DEFAULT 0,
            users_reviewed INTEGER DEFAULT 0,
            training_assigned INTEGER DEFAULT 0,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database schema initialized.")
