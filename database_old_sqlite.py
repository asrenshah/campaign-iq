import sqlite3
import json
from datetime import datetime

DB_NAME = "campaigns.db"


def get_connection():
    """Buka sambungan ke database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Cipta jadual jika belum wujud."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            data TEXT NOT NULL,
            user_id INTEGER
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialized: campaigns.db")


def init_user_table():
    """Cipta jadual users jika belum wujud."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Users table initialized")


def save_analysis(result):
    """Simpan satu analisis ke database (tanpa user_id)."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO analyses (timestamp, data)
        VALUES (?, ?)
    """, (
        datetime.now().isoformat(),
        json.dumps(result)
    ))

    conn.commit()
    conn.close()


def save_analysis_with_user(user_id, result):
    """Simpan satu analisis ke database dengan user_id."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO analyses (timestamp, data, user_id)
        VALUES (?, ?, ?)
    """, (
        datetime.now().isoformat(),
        json.dumps(result),
        user_id
    ))

    conn.commit()
    conn.close()


def get_history(limit=50):
    """Dapatkan senarai analisis terkini (tanpa filter user)."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, timestamp, data FROM analyses
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    history = []
    for row in rows:
        data = json.loads(row["data"])
        history.append({
            "id": row["id"],
            "timestamp": row["timestamp"],
            "data": data
        })

    return history


def get_history_by_user(user_id, limit=50):
    """Dapatkan senarai analisis untuk user tertentu."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, timestamp, data FROM analyses
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT ?
    """, (user_id, limit))

    rows = cursor.fetchall()
    conn.close()

    history = []
    for row in rows:
        data = json.loads(row["data"])
        history.append({
            "id": row["id"],
            "timestamp": row["timestamp"],
            "data": data
        })

    return history


def get_user_by_email(email):
    """Dapatkan user berdasarkan email."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, email FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {"id": row["id"], "email": row["email"]}
    return None


def create_user(email):
    """Cipta user baru."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT OR IGNORE INTO users (email) VALUES (?)", (email,))
    conn.commit()
    conn.close()

    return get_user_by_email(email)


def get_analysis_by_id(analysis_id):
    """Dapatkan satu analisis lengkap."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, timestamp, data FROM analyses
        WHERE id = ?
    """, (analysis_id,))

    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "id": row["id"],
            "timestamp": row["timestamp"],
            "data": json.loads(row["data"])
        }

    return None


def delete_analysis_by_id(row_id):
    """Padam satu analisis."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM analyses WHERE id = ?", (row_id,))
    conn.commit()
    conn.close()


def delete_all_history():
    """Padam semua analisis."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM analyses")
    conn.commit()
    conn.close()


def get_stats():
    """Dapatkan statistik ringkas."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM analyses")
    total = cursor.fetchone()["total"]

    conn.close()

    return {
        "total_analyses": total
    }


def search_history(keyword):
    """Cari dalam CEO summary atau campaigns."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, timestamp, data FROM analyses
        WHERE data LIKE ?
        ORDER BY id DESC
    """, (f"%{keyword}%",))

    rows = cursor.fetchall()
    conn.close()

    history = []
    for row in rows:
        data = json.loads(row["data"])
        history.append({
            "id": row["id"],
            "timestamp": row["timestamp"],
            "data": data
        })

    return history