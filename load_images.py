import os
import sqlite3

def load_images_to_db():
    # Подключение к базе данных
    conn = sqlite3.connect('DataBaseImgTest.db')
    cursor = conn.cursor()

    # Получаем список папок с изображениями (например, post_1, post_2, ...)
    posts_dir = 'img_bd'
    post_folders = [f for f in os.listdir(posts_dir) if os.path.isdir(os.path.join(posts_dir, f))]

    # Проходим по каждой папке
    for folder in post_folders:
        media_links = []

        # Получаем список файлов изображений в папке
        folder_path = os.path.join(posts_dir, folder)
        images = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.png'))]

        # Создаем строку с путями к изображениям
        media_links = ', '.join(images)

        # Вставляем записи в таблицу telegram
        cursor.execute('''
        INSERT INTO telegram (media, processing) VALUES (?, ?)
        ''', (media_links, 0))

    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()

if __name__ == '__main__':
    load_images_to_db()
