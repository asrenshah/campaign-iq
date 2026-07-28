import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


# ============================================
# CONNECTION
# ============================================

def get_connection():
    return psycopg2.connect(
        os.environ["DATABASE_URL"]
    )


# ============================================
# INIT TABLES (TANPA DROP)
# ============================================

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        full_name TEXT,
        company_name TEXT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS analyses (
        id SERIAL PRIMARY KEY,
        timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        data JSONB NOT NULL,
        user_id INTEGER REFERENCES users(id) ON DELETE SET NULL
    );
    """)

    conn.commit()
    cur.close()
    conn.close()

    print("✅ PostgreSQL tables initialized")


# ============================================
# USER
# ============================================

def get_user_by_email(email):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        """
        SELECT
            id,
            full_name,
            company_name,
            email,
            password
        FROM users
        WHERE email=%s
        """,
        (email,)
    )

    user = cur.fetchone()

    cur.close()
    conn.close()

    return user


def create_user(full_name, company_name, email, password):
    conn = get_connection()
    cur = conn.cursor()

    hashed = generate_password_hash(password)

    cur.execute("""
        INSERT INTO users
        (full_name, company_name, email, password)
        VALUES (%s,%s,%s,%s)
        ON CONFLICT (email) DO NOTHING
    """,
    (
        full_name,
        company_name,
        email,
        hashed
    ))

    conn.commit()

    cur.close()
    conn.close()

    return get_user_by_email(email)


def verify_user(email, password):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        """
        SELECT
            id,
            full_name,
            company_name,
            email,
            password
        FROM users
        WHERE email=%s
        """,
        (email,)
    )

    user = cur.fetchone()

    cur.close()
    conn.close()

    if not user:
        return None

    if check_password_hash(user["password"], password):
        return user

    return None


# ============================================
# SAVE ANALYSIS (TANPA TIMESTAMP)
# ============================================

def save_analysis(user_id, result):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO analyses
        (data, user_id)
        VALUES (%s, %s)
    """,
    (
        Json(result),
        user_id
    ))

    conn.commit()

    cur.close()
    conn.close()


# ============================================
# HISTORY ALL
# ============================================

def get_history(limit=50):

    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT id, timestamp, data
        FROM analyses
        ORDER BY id DESC
        LIMIT %s
    """,
    (limit,))

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows


# ============================================
# HISTORY USER
# ============================================

def get_history_by_user(user_id, limit=50):

    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT id, timestamp, data
        FROM analyses
        WHERE user_id=%s
        ORDER BY id DESC
        LIMIT %s
    """,
    (user_id, limit))

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows


# ============================================
# DELETE ONE
# ============================================

def delete_analysis(row_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM analyses
        WHERE id=%s
    """,
    (row_id,))

    conn.commit()

    cur.close()
    conn.close()


# ============================================
# DELETE ALL
# ============================================

def delete_all_history():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM analyses
    """)

    conn.commit()

    cur.close()
    conn.close()