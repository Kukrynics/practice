import os
import shutil
import sqlite3

def copy_selected_images():
    # Папка для сохранения выбранных картинок
    base_dir = 'select_img'

    # Проверяем, существует ли папка select_img
    if os.path.exists(base_dir):
        # Удаляем папку и все её содержимое
        shutil.rmtree(base_dir)

    # Создаем новую пустую папку select_img
    os.makedirs(base_dir)

    # Подключаемся к базе данных
    conn = sqlite3.connect('DataBaseImgTest.db')
    cursor = conn.cursor()

    # Извлекаем все записи из таблицы best_img
    cursor.execute("SELECT group_id, media FROM best_img")
    rows = cursor.fetchall()

    # Для каждой группы создаем папку и копируем картинки
    for row in rows:
        group_id = row[0]
        media = row[1].split(", ")  # Список путей к картинкам

        # Создаем папку для группы
        group_dir = os.path.join(base_dir, f'group_{group_id}')
        if not os.path.exists(group_dir):
            os.makedirs(group_dir)

        # Копируем все изображения в соответствующую папку
        for img_path in media:
            if os.path.exists(img_path):  # Проверяем, существует ли изображение
                # Получаем имя файла
                img_name = os.path.basename(img_path)

                # Если файл с таким именем уже существует, изменим имя
                new_path = os.path.join(group_dir, img_name)

                # Добавляем уникальный идентификатор, если файл с таким именем уже существует
                counter = 1
                while os.path.exists(new_path):
                    new_name = f"{os.path.splitext(img_name)[0]}_{counter}{os.path.splitext(img_name)[1]}"
                    new_path = os.path.join(group_dir, new_name)
                    counter += 1

                # Копируем изображение
                shutil.copy(img_path, new_path)

    # Закрываем соединение с БД
    conn.close()

if __name__ == '__main__':
    copy_selected_images()
