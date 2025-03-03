import psycopg2
from config import DATABASE_CONFIG

def get_connection():
    """
    Устанавливает соединение с базой данных PostgreSQL.
    Возвращает объект соединения.
    """
    return psycopg2.connect(**DATABASE_CONFIG)

def fetch_images():
    """
    Извлекает из базы данных все записи, где маркер равен False.
    Возвращает список кортежей (id, медиа).
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, media FROM posts WHERE marker = False")
    return cursor.fetchall()

def update_marker(post_id, marker):
    """
    Обновляет маркер для конкретного поста.
    :param post_id: ID поста
    :param marker: Новое значение маркера (True или Copy)
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE posts SET marker = %s WHERE id = %s", (marker, post_id))
    conn.commit()

def save_feature_vector(post_id, feature_vector):
    """
    Сохраняет вектор признаков изображения в базу данных.
    :param post_id: ID поста
    :param feature_vector: Вектор признаков (список или массив numpy)
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE posts SET feature_vector = %s WHERE id = %s", (feature_vector.tolist(), post_id))
    conn.commit()