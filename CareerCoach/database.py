import sqlite3
import hashlib
import secrets
from datetime import datetime

DB_PATH = "careercoach.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            candidate_number TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_number TEXT NOT NULL,
            role TEXT,
            level TEXT,
            score REAL,
            status TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def make_candidate_number():
    return "CC-" + secrets.token_hex(3).upper()

def create_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    candidate = make_candidate_number()
    try:
        cur.execute(
            "INSERT INTO users(username,password_hash,candidate_number,created_at) VALUES(?,?,?,?)",
            (username, hash_password(password), candidate, datetime.now().isoformat())
        )
        conn.commit()
        return candidate
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def authenticate(username, password):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT username,candidate_number FROM users WHERE username=? AND password_hash=?",
        (username, hash_password(password))
    )
    row = cur.fetchone()
    conn.close()
    return {"username": row[0], "candidate_number": row[1]} if row else None

def save_interview(candidate_number, role, level, score, status):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO interviews(candidate_number,role,level,score,status,created_at) VALUES(?,?,?,?,?,?)",
        (candidate_number, role, level, score, status, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
