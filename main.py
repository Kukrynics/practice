import sqlite3
from process_images import process_images_for_group
from select_best_images import select_best_images_for_group

def main():
    # Подключаемся к базе данных
    conn = sqlite3.connect('DataBaseImgTest.db')
    cursor = conn.cursor()

    # Извлекаем все уникальные group_id
    cursor.execute('SELECT DISTINCT group_id FROM telegram')
    group_ids = cursor.fetchall()

    # Обрабатываем каждую группу
    for group_id in group_ids:
        group_id = group_id[0]

        # 1. Обрабатываем изображения для группы
        process_images_for_group(group_id)

        # 2. Выбираем лучшие изображения для группы
        select_best_images_for_group()

    conn.close()

if __name__ == '__main__':
    main()
