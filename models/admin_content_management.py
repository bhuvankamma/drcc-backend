# models.py

from database.database import get_connection
from datetime import datetime


# ✅ CREATE TABLE FUNCTION
def create_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS content (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            type VARCHAR(100) NOT NULL,
            content TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()


def get_all_content():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM content ORDER BY id;")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_content_by_id(content_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM content WHERE id = %s;", (content_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def update_content(content_id: int, new_content: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE content
        SET content = %s,
            updated_at = %s
        WHERE id = %s
        RETURNING *;
        """,
        (new_content, datetime.now(), content_id),
    )
    updated_row = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return updated_row