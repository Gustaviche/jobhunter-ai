import sqlite3
from pathlib import Path

DB_PATH = Path("data/jobs.db")


def init_db():
    DB_PATH.parent.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT,
            location TEXT,
            contract_type TEXT,
            url TEXT,
            description TEXT,
            status TEXT DEFAULT 'À postuler',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            username TEXT       )
    """)

    conn.commit()
    conn.close()


def add_job(title, company, location, contract_type, url, description,username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO jobs (
            title, company, location, contract_type, url, description, username
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (title, company, location, contract_type, url, description, username))

    conn.commit()
    conn.close()


def get_jobs(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, company, location, contract_type, status, created_at
        FROM jobs
        WHERE username = ?
        ORDER BY created_at DESC
    """, (username,))

    jobs = cursor.fetchall()
    conn.close()



    return jobs

def get_job_by_id(job_id, username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, company, location, contract_type, url, description, status, created_at, cover_message
        FROM jobs
        WHERE id = ? AND username = ?
    """, (job_id, username))

    job = cursor.fetchone()
    conn.close()

    return job

def update_job_status(job_id, status,username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE jobs
        SET status = ?
        WHERE id = ? AND username = ?
    """, (status, job_id, username))

    conn.commit()
    conn.close()

def add_cover_message_column():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("ALTER TABLE jobs ADD COLUMN cover_message TEXT")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()


def update_cover_message(job_id, cover_message,username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE jobs
        SET cover_message = ?
        WHERE id = ? AND username = ?
    """, (cover_message, job_id, username))

    conn.commit()
    conn.close()

def delete_job(job_id, username):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM jobs
        WHERE id = ? AND username = ?
    """, (job_id, username))

    conn.commit()
    conn.close()