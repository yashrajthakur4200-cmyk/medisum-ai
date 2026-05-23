import sqlite3

DB_NAME = "medisum.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
   
                   CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        input_text TEXT,
        summary TEXT,
        severity_level TEXT,
        severity_score INTEGER,
        recommendation TEXT,
        suggested_doctors TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")


    conn.commit()
    conn.close()


def insert_report(text, summary, severity_level, severity_score, recommendation, suggested_doctors):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO reports
    (input_text, summary, severity_level, severity_score, recommendation, suggested_doctors)
    VALUES (?, ?, ?, ?, ?, ?)
""", (text, summary, severity_level, severity_score, recommendation, suggested_doctors))


    conn.commit()
    conn.close()


def fetch_reports():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, summary, severity_level, severity_score,
       recommendation, suggested_doctors, created_at

        FROM reports ORDER BY created_at DESC
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows

