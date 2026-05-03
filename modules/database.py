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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def add_job(title, company, location, contract_type, url, description):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO jobs (
            title, company, location, contract_type, url, description
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (title, company, location, contract_type, url, description))

    conn.commit()
    conn.close()


def get_jobs():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, company, location, contract_type, status, created_at
        FROM jobs
        ORDER BY created_at DESC
    """)

    jobs = cursor.fetchall()
    conn.close()



    return jobs

def get_job_by_id(job_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, company, location, contract_type, url, description, status, created_at, cover_message
        FROM jobs
        WHERE id = ?
    """, (job_id,))

    job = cursor.fetchone()
    conn.close()

    return job

def update_job_status(job_id, status):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE jobs
        SET status = ?
        WHERE id = ?
    """, (status, job_id))

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


def update_cover_message(job_id, cover_message):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE jobs
        SET cover_message = ?
        WHERE id = ?
    """, (cover_message, job_id))

    conn.commit()
    conn.close()

def delete_job(job_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM jobs
        WHERE id = ?
    """, (job_id,))

    conn.commit()
    conn.close()