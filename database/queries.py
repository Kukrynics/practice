# database/queries.py
import psycopg2

from database.db import get_connection

def insert_news(title, content, source, url, published_at):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO news (title, content, source, url, published_at)
        VALUES (%s, %s, %s, %s, %s)
        """, (title, content, source, url, published_at))
        conn.commit()
    except psycopg2.IntegrityError:
        conn.rollback()  # Ignore duplicates
    finally:
        cursor.close()
        conn.close()
