"""
Database Setup and Connection Management for AI-Enhanced Admission Management System
Uses SQLite with optimized WAL mode and schema initialization.
Also provides password reset helpers.
"""

import sqlite3
import os
import hashlib
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'admissions.db')

def get_db_connection():
    """Returns a SQLite connection with Row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def hash_password(password: str) -> str:
    """Returns SHA256 hashed password with a secure salt."""
    salt = "institutional_adm_sec_2026"
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

def init_db():
    """Initializes database tables if they do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('student', 'admin')),
        phone TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # 2. Courses table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        department TEXT NOT NULL,
        seats INTEGER NOT NULL,
        min_gpa REAL NOT NULL,
        min_entrance REAL NOT NULL
    );
    """)
    
    # 3. Applications table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        application_no TEXT UNIQUE NOT NULL,
        user_id INTEGER NOT NULL,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        dob TEXT NOT NULL,
        gender TEXT NOT NULL,
        address TEXT,
        course_code TEXT NOT NULL,
        academic_gpa REAL NOT NULL,
        entrance_score REAL NOT NULL,
        attendance_pct REAL NOT NULL,
        prev_academic_score REAL NOT NULL,
        category TEXT NOT NULL CHECK(category IN ('General', 'OBC', 'SC_ST', 'EWS')),
        extracurricular TEXT NOT NULL CHECK(extracurricular IN ('None', 'School_Level', 'State_Level', 'National_Level')),
        document_path TEXT,
        document_name TEXT,
        status TEXT NOT NULL DEFAULT 'Submitted' CHECK(status IN ('Submitted', 'Under Review', 'Approved', 'Rejected', 'Waitlisted')),
        ml_prediction TEXT,
        ml_probability REAL,
        ai_evaluation_summary TEXT,
        ai_recommendation TEXT,
        ai_profile_insights TEXT,
        ai_explanation TEXT,
        admin_remarks TEXT,
        reviewed_by TEXT,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (course_code) REFERENCES courses(code) ON UPDATE CASCADE
    );
    """)
    
    # 4. Password Resets table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS password_resets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        reset_code TEXT NOT NULL,
        expires_at TIMESTAMP NOT NULL,
        used INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    conn.commit()
    conn.close()
    print("Database tables initialized successfully.")

def save_sqlite_reset_code(email: str, code: str, expires_in_minutes: int = 15):
    """Saves a password reset verification code for an email."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Invalidate previous unused codes
    cursor.execute("UPDATE password_resets SET used = 1 WHERE email = ? AND used = 0", (email,))
    
    expires_at = datetime.now() + timedelta(minutes=expires_in_minutes)
    cursor.execute("""
    INSERT INTO password_resets (email, reset_code, expires_at, used)
    VALUES (?, ?, ?, 0)
    """, (email, code, expires_at.strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()

def verify_and_use_sqlite_reset_code(email: str, code: str) -> bool:
    """Verifies reset code for email and marks as used if valid and not expired."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("""
    SELECT id FROM password_resets 
    WHERE email = ? AND reset_code = ? AND used = 0 AND expires_at > ?
    ORDER BY id DESC LIMIT 1
    """, (email, code, now_str))
    row = cursor.fetchone()
    
    if row:
        cursor.execute("UPDATE password_resets SET used = 1 WHERE id = ?", (row['id'],))
        conn.commit()
        conn.close()
        return True
    
    conn.close()
    return False

def update_sqlite_user_password(email: str, new_password_hash: str) -> bool:
    """Updates user's password in SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password_hash = ? WHERE email = ?", (new_password_hash, email))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected > 0

if __name__ == '__main__':
    init_db()
